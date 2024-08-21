from __future__ import annotations

import sqlite3
from typing import Literal, overload
from .utils import get_product_pictures
from fuzzywuzzy import fuzz
VALID_STARS = Literal[1, 2, 3, 4, 5]
PRODUCT_ID = int
QUANTITY = int


class Product:
    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        id: int,
        name: str,
        price: float,
        description: str,
        image_dir: str,
        stock: int,
    ):
        self.__conn = connection
        self.id = id
        self.name = name
        self.price = price
        self.description = description
        self.image_dir = get_product_pictures(id)
        self.stock = stock

    def add_review(self, *, user_id: int, stars: VALID_STARS, review: str | None):
        query = r"INSERT INTO REVIEWS (`USER_ID`, `PRODUCT_ID`, `STARS`, `REVIEW`) VALUES (?, ?, ?, ?)"
        cursor = self.__conn.cursor()
        cursor.execute(query, (user_id, self.id, stars, review))
        self.__conn.commit()

    def del_review(self, *, user_id: int) -> None:
        query = r"DELETE FROM REVIEWS WHERE `USER_ID` = ? AND `PRODUCT_ID` = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (user_id, self.id))
        self.__conn.commit()

    def is_available(self, count: QUANTITY = 1) -> bool:
        query = r"SELECT STOCK FROM PRODUCTS WHERE ID = ? AND STOCK >= ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.id, count))
        stock = cursor.fetchone()

        if stock is None:
            return False

        stock = stock[0]
        return stock > count

    def use(self, count: QUANTITY = 1) -> None:
        query = r"UPDATE PRODUCTS SET STOCK = STOCK - ? WHERE ID = ? AND STOCK >= ?"
        cursor = self.__conn.cursor()

        cursor.execute(query, (count, self.id, count))
        updated = cursor.rowcount

        if updated == 0:
            error = "Product is not available."
            raise ValueError(error)

        self.__conn.commit()

    def release(self, count: QUANTITY = 1) -> None:
        query = r"UPDATE PRODUCTS SET STOCK = STOCK + ? WHERE ID = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (count, self.id))
        self.__conn.commit()

    @classmethod
    def create(
        cls,
        connection: sqlite3.Connection,
        *,
        name: str,
        price: float,
        description: str,
        image_dir: str,
        stock: int = 0,
    ) -> Product:
        cursor = connection.cursor()
        query = r"""
            INSERT INTO PRODUCTS (NAME, PRICE, DESCRIPTION, IMAGE_DIR, STOCK) VALUES (?, ?, ?, ?, ?)
            RETURNING *
        """
        result = cursor.execute(query, (name, price, description, image_dir, stock))
        data = result.fetchone()
        connection.commit()

        return cls(connection, **data)

    @classmethod
    def from_id(cls, connection: sqlite3.Connection, product_id: PRODUCT_ID) -> Product:
        query = r"SELECT * FROM PRODUCTS WHERE ID = ?"
        cursor = connection.cursor()
        cursor.execute(query, (product_id,))
        row = cursor.fetchone()
        if row is None:
            error = "Product not found."
            raise ValueError(error) from None
        return cls(connection, **row)
    
    @classmethod
    def all(cls, connection: sqlite3.Connection) -> list[Product]:
        query = r"SELECT * FROM PRODUCTS"
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [cls(connection, **row) for row in rows]

    @classmethod
    def search(cls, connection: sqlite3.Connection, query: str) -> list[Product]:
        all_products = cls.all(connection)
        fuzz_sort = sorted(
            all_products,
            key=lambda product: fuzz.partial_ratio(query, product.name),
            reverse=True,
        )
        return fuzz_sort


    def json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "image_dir": self.image_dir,
            "stock": self.stock,
        }

class Cart:
    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        user_id: int,
    ):
        self.__conn = connection
        self.user_id = user_id
        self._products: dict[PRODUCT_ID, QUANTITY] = {}

        self.init()

    def get_product(self, product_id: PRODUCT_ID) -> Product:
        return Product.from_id(self.__conn, product_id)

    @overload
    def get_products(self, json: Literal[False]) -> dict[Product, QUANTITY]: ...

    @overload
    def get_products(self, json: Literal[True]) -> list: ...

    def get_products(self, json: bool = False) -> dict[Product, QUANTITY] | list:
        if not json:
            return [
                self.get_product(product_id).json()
                for product_id, _ in self._products.items()
            ]

        return {
            self.get_product(product_id): quantity
            for product_id, quantity in self._products.items()
        }

    def init(self) -> None:
        query = r"SELECT PRODUCT_ID, QUANTITY FROM CARTS WHERE USER_ID = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.user_id,))
        rows = cursor.fetchall()
        self._products = {product_id: quantity for product_id, quantity in rows}

    def add_product(self, *, product: Product, quantity: QUANTITY = 1) -> None:
        if not product.is_available(quantity):
            error = "Product is not available."
            raise ValueError(error)

        if product.id in self._products:
            self._products[product.id] += quantity
        else:
            self._products[product.id] = quantity

        product.use(quantity)

    def remove_product(self, *, product: Product, quantity: QUANTITY = 1) -> None:
        if product.id in self._products:
            if self._products[product.id] <= 0:
                del self._products[product.id]
            else:
                self._products[product.id] -= quantity
        else:
            error = "Product not found in cart."
            raise ValueError(error)

        product.release(quantity)

    def _sql_update_cart(self) -> None:
        query = r"INSERT OR REPLACE INTO CARTS (USER_ID, PRODUCT_ID, QUANTITY) VALUES (?, ?, ?)"
        cursor = self.__conn.cursor()

        for product_id, quantity in self._products.items():
            cursor.execute(query, (self.user_id, product_id, quantity))

        self.__conn.commit()

    def update_to_database(self) -> None:
        self._sql_update_cart()

        query = r"""
            INSERT INTO ORDERS (USER_ID, PRODUCT_ID, QUANTITY, TOTAL_PRICE)
                SELECT USER_ID, PRODUCT_ID, QUANTITY, QUANTITY * (SELECT PRICE FROM PRODUCTS WHERE ID = PRODUCT_ID)
                FROM CARTS
                WHERE USER_ID = ?
        """

        cursor = self.__conn.cursor()

        try:
            cursor.execute(r"BEGIN TRANSACTION")
            cursor.execute(query, (self.user_id,))
            cursor.execute(r"DELETE FROM CARTS WHERE USER_ID = ?", (self.user_id,))
            cursor.execute(r"COMMIT")
        except sqlite3.Error as e:
            cursor.execute(r"ROLLBACK")
            raise e

    def clear(self, *, product: Product | None = None) -> None:
        if product is None:
            self._products.clear()
            return

        if product.id in self._products:
            count = self._products[product.id]
            del self._products[product.id]
            product.release(count)
        else:
            error = "Product not found in cart."
            raise ValueError(error)
