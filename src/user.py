from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .order import Order
    from .product import VALID_STARS, Cart, Product
    from .type_hints import Client as RazorpayClient
    from .type_hints import RazorPayOrderDict

from .utils import Password


class User:
    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        id: int,
        email: str,
        name: str,
        password: str,
        created_at: str | None = None,
        role: str = "USER",
        address: str,
        phone: str,
    ):
        self.__conn = connection
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        self.created_at = datetime.fromisoformat(created_at) if created_at else None
        self.address = address
        self.phone = phone

        self.is_active = True
        self.is_anonymous = False
        self.is_authenticated = True
    
    def get_id(self):
        return str(self.id)

    @property
    def is_admin(self):
        return False

    @property
    def role(self):
        return "USER"

    @property
    def cart(self) -> Cart:
        from .product import Cart

        return Cart(self.__conn, user_id=self.id)

    def __str__(self) -> str:
        return (
            f"User(id={self.id!r} email={self.email!r} created_at={self.created_at!r})"
        )

    @classmethod
    def from_email(
        cls, connection: sqlite3.Connection, *, email: str, password: str
    ) -> User:
        cursor = connection.cursor()
        query = r"""
            SELECT * FROM USERS WHERE EMAIL = ? AND PASSWORD = ?
        """
        hashed_password = Password(password)

        cursor.execute(
            query,
            (email, hashed_password.hex),
        )
        row = cursor.fetchone()
        if row is None:
            error = "User not found. Either email or password is incorrect."
            raise ValueError(error) from None
        return cls(connection, **row)

    @classmethod
    def from_id(cls, connection: sqlite3.Connection, user_id: int):
        cursor = connection.cursor()
        query = r"""
            SELECT * FROM USERS WHERE ID = ?
        """
        cursor.execute(
            query,
            (int(user_id),),
        )
        row = cursor.fetchone()
        if row is None:
            error = "User not found."
            raise ValueError(error) from None
        return cls(connection, **row)

    @classmethod
    def create(
        cls,
        connection: sqlite3.Connection,
        *,
        email: str,
        name: str,
        password: str,
        address: str,
        phone: str,
        role: str = "user",
    ) -> User:
        cursor = connection.cursor()
        query = r"""
            INSERT INTO USERS (EMAIL, PASSWORD, NAME, ADDRESS, PHONE)
                VALUES (?, ?, ?, ?, ?)
            RETURNING *
        """

        hashed_password = Password(password)

        result = cursor.execute(
            query, (email, hashed_password.hex, name, address, phone)
        )
        data = result.fetchone()
        connection.commit()

        return cls(connection, **data)

    def add_review(self, *, product: Product, stars: VALID_STARS, review: str | None):
        product.add_review(user_id=self.id, stars=stars, review=review)

    def del_review(self, *, product: Product) -> None:
        product.del_review(user_id=self.id)

    def add_to_cart(self, *, product: Product, quantity: int = 1) -> None:
        self.cart.add_product(product=product, quantity=quantity)

    def remove_from_cart(self, *, product: Product, quantity: int = 1) -> None:
        self.cart.remove_product(product=product, quantity=quantity)

    def clear_cart(self, *, product: Product | None = None) -> None:
        self.cart.clear(product=product)

    def add_to_fav(self, *, product: Product) -> None:
        query = r"INSERT INTO FAVOURITES (USER_ID, PRODUCT_ID) VALUES (?, ?)"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.id, product.id))

        self.__conn.commit()

    def partial_checkout(self) -> list[Order]:
        from .order import Order

        self.cart.update_to_database()
        self.clear_cart()

        orders: list[Order] = []
        query = r"SELECT * FROM ORDERS WHERE USER_ID = ? AND STATUS = 'PEND'"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.id,))

        while row := cursor.fetchone():
            orders.append(Order(self.__conn, **row))

        # cursor.execute("UPDATE `ORDERS` SET `STATUS` = 'CONF' WHERE `USER_ID` = ? AND `STATUS` = 'PEND'", (self.id,))
        # self.__conn.commit()

        return orders

    def full_checkout(self, razorpay_client: RazorpayClient) -> RazorPayOrderDict:
        orders = self.partial_checkout()

        if not orders:
            error = "No orders found to checkout."
            raise ValueError(error)

        total_price = sum(order.total_price for order in orders)
        notes = {}

        for order in orders:
            notes[order.product.name] = {
                "quantity": order.quantity,
                "price": order.product.price,
            }

        final_payload = {
            "amount": int(total_price * 100),
            "currency": "INR",
            "notes": notes,
        }

        api_response: dict = razorpay_client.order.create(final_payload)
        order_id = api_response["id"]

        query = r"""
            UPDATE `ORDERS` 
            SET `RAZORPAY_ORDER_ID` = ?, `STATUS` = 'CONF'
            WHERE `USER_ID` = ? AND `STATUS` = 'PEND'
        """
        cursor = self.__conn.cursor()
        update = cursor.execute(query, (order_id, self.id))

        if update.rowcount == 0:
            error = "No orders found to checkout."
            raise ValueError(error)

        self.__conn.commit()

        assert self.__check_api_response(
            full_paylaod=final_payload, api_response=api_response
        )

        return api_response  # type: ignore

    def __check_api_response(self, *, full_paylaod: dict, api_response: dict) -> bool:
        amount_correct = full_paylaod["amount"] == api_response["amount"]
        currency_correct = full_paylaod["currency"] == api_response["currency"]
        notes_correct = full_paylaod["notes"] == api_response["notes"]
        status_correct = api_response["status"] == "created"

        return amount_correct and currency_correct and notes_correct and status_correct

    @staticmethod
    def exists(connection: sqlite3.Connection, email: str) -> bool:
        cursor = connection.cursor()
        query = r"""
            SELECT 1 FROM USERS WHERE EMAIL = ?
        """
        cursor.execute(query, (email,))
        return cursor.fetchone() is not None

class Admin(User):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def role(self):
        return "ADMIN"

    @property
    def is_admin(self):
        return True
