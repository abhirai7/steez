from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Literal

import arrow

from .utils import SQLITE_OLD

if TYPE_CHECKING:
    from .product import Product
    from .user import User


VALID_STATUS = Literal["PEND", "CONF", "PAID", "COD"]
# PEND - Pending
# CONF - Confirmed
# PAID - Paid
# COD - Cash on Delivery

class Order:
    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        id: int,
        user_id: int,
        product_id: int,
        quantity: int,
        total_price: float,
        created_at: str,
        status: str = "PEND",
        razorpay_order_id: str | None = None,
    ) -> None:
        self.connection = connection
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
        self.total_price = total_price
        self.created_at = arrow.get(created_at)
        self.status = status
        self.razorpay_order_id = razorpay_order_id

    def is_recent(self, days: int = 7) -> bool:
        return self.created_at > arrow.utcnow().shift(days=-days)

    @classmethod
    def create(
        cls,
        connection: sqlite3.Connection,
        user_id: int,
        product_id: int,
        quantity: int,
        total_price: float,
    ) -> Order:
        cursor = connection.cursor()
        if SQLITE_OLD:
            cursor.execute(
                "INSERT INTO ORDERS (USER_ID, PRODUCT_ID, QUANTITY, TOTAL_PRICE) VALUES (?, ?, ?, ?)",
                (user_id, product_id, quantity, total_price),
            )
            result = cursor.execute(
                "SELECT * FROM ORDERS WHERE ROWID = ?", (cursor.lastrowid,)
            )
        else:
            result = cursor.execute(
                "INSERT INTO ORDERS (USER_ID, PRODUCT_ID, QUANTITY, TOTAL_PRICE) VALUES (?, ?, ?, ?) RETURNING *",
                (user_id, product_id, quantity, total_price),
            )

        row = result.fetchone()
        connection.commit()
        return cls(connection, **row)

    @classmethod
    def from_id(cls, connection: sqlite3.Connection, order_id: int) -> Order:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ORDERS WHERE ID = ?", (order_id,))
        row = cursor.fetchone()
        if row is None:
            error = "Order not found."
            raise ValueError(error) from None
        return cls(connection, **row)

    @classmethod
    def from_razorpay_order_id(
        cls, connection: sqlite3.Connection, razorpay_order_id: str
    ) -> Order:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM ORDERS WHERE RAZORPAY_ORDER_ID = ?", (razorpay_order_id,)
        )
        row = cursor.fetchone()
        if row is None:
            error = "Order not found."
            raise ValueError(error) from None
        return cls(connection, **row)

    @property
    def user(self) -> User:
        from .user import User

        return User.from_id(self.connection, self.user_id)

    @property
    def product(self) -> Product:
        from .product import Product

        return Product.from_id(self.connection, self.product_id)

    @classmethod
    def all(
        cls,
        connection: sqlite3.Connection,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Order]:
        cursor = connection.cursor()

        if limit is None:
            query = r"SELECT * FROM ORDERS"
            cursor.execute(query)
        else:
            query = r"SELECT * FROM ORDERS LIMIT ? OFFSET ?"
            cursor.execute(query, (limit, offset))

        rows = cursor.fetchall()
        return [cls(connection, **row) for row in rows]

    @classmethod
    def total_count(cls, connection: sqlite3.Connection) -> int:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM ORDERS")
        return cursor.fetchone()[0]

    def update_order_status(
        self, *, status: VALID_STATUS, razorpay_order_id: str
    ) -> None:
        cursor = self.connection.cursor()
        assert razorpay_order_id == self.razorpay_order_id

        cursor.execute(
            r"UPDATE ORDERS SET STATUS = ? WHERE RAZORPAY_ORDER_ID = ? AND ID = ? AND STATUS = 'CONF' AND USER_ID = ?",
            (status, razorpay_order_id, self.id, self.user_id),
        )
        self.connection.commit()
        self.status = status
        self.razorpay_order_id = razorpay_order_id

    @classmethod
    def delete(
        cls, connection: sqlite3.Connection, *, order_id: int, user_id: int
    ) -> None:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM ORDERS WHERE ID = ? AND STATUS != 'PAID' AND USER_ID = ?",
            (order_id, user_id),
        )
        connection.commit()
