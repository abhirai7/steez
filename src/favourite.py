from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product
    from .user import User

import sqlite3


class Favourite:
    def __init__(self, conn: sqlite3.Connection, *, id: int, user_id: int, product_unique_id: str) -> None:
        self.__conn = conn
        self.id = id
        self.user_id = user_id
        self.product_unique_id = product_unique_id
        self.__user: User | None = None
        self.__product: Product | None = None

    @property
    def user(self) -> User:
        if self.__user is None:
            from .user import User

            self.__user = User.from_id(self.__conn, self.user_id)

        return self.__user

    @property
    def product(self) -> Product:
        if self.__product is None:
            from .product import Product

            self.__product = Product.from_unique_id(self.__conn, self.product_unique_id)[0]

        return self.__product

    def delete(self) -> None:
        query = r"DELETE FROM FAVOURITES WHERE ID = ?"

        cursor = self.__conn.cursor()
        cursor.execute(query, (self.id,))

        self.__conn.commit()

    @classmethod
    def from_id(cls, conn: sqlite3.Connection, id: int) -> Favourite:
        query = r"SELECT ID, USER_ID, PRODUCT_UNIQUE_ID FROM FAVOURITES WHERE ID = ?"

        cursor = conn.cursor()
        cursor.execute(query, (id,))

        row = cursor.fetchone()
        if row is None:
            error = "Favourite does not exist"
            raise ValueError(error)

        return cls(conn, **row)

    @classmethod
    def add(cls, conn: sqlite3.Connection, *, user: User, product: Product) -> Favourite:
        query = r"INSERT INTO FAVOURITES (USER_ID, PRODUCT_UNIQUE_ID) VALUES (?, ?) RETURNING *"

        cursor = conn.cursor()
        cursor.execute(query, (user.id, product.unique_id))
        data = cursor.fetchone()
        conn.commit()

        return cls(conn, **data)

    @classmethod
    def all(cls, conn: sqlite3.Connection) -> list[Favourite]:
        query = r"SELECT * FROM FAVOURITES ORDER BY USER_ID"

        cursor = conn.cursor()
        cursor.execute(query)

        return [cls(conn, **row) for row in cursor.fetchall()]

    @classmethod
    def from_user(cls, conn: sqlite3.Connection, *, user: User, product: Product) -> list[Favourite]:
        query = r"""
            SELECT * FROM FAVOURITES WHERE USER_ID = ? AND PRODUCT_UNIQUE_ID = ?
        """
        cursor = conn.cursor()
        cursor.execute(query, (user.id, product.unique_id))

        return [cls(conn, **row) for row in cursor.fetchall()]

    @classmethod
    def exists(cls, conn: sqlite3.Connection, *, user: User, product: Product) -> bool:
        query = r"SELECT * FROM FAVOURITES WHERE USER_ID = ? AND PRODUCT_UNIQUE_ID = ?"

        cursor = conn.cursor()
        cursor.execute(query, (user.id, product.id))

        return cursor.fetchone() is not None
