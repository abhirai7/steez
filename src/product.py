from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Literal

from fuzzywuzzy import fuzz

from .utils import generate_gift_card_code, get_product_pictures, size_names

VALID_STARS = Literal[1, 2, 3, 4, 5]
PRODUCT_ID = int
QUANTITY = int

if TYPE_CHECKING:
    from .user import User


class Review:
    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        id: int,
        user_id: int,
        product_id: int,
        review: str | None = None,
        stars: VALID_STARS,
        created_at: str | None = None,
    ):
        self.__conn = connection
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.stars = stars
        self.review = review
        self.created_at = created_at

    @property
    def user(self) -> User:
        from .user import User

        return User.from_id(self.__conn, self.user_id)

    @property
    def product(self) -> Product:
        return Product.from_id(self.__conn, self.product_id)

    @classmethod
    def create(
        cls,
        connection: sqlite3.Connection,
        *,
        user_id: int,
        product_id: int,
        review: str,
        stars: VALID_STARS,
    ) -> Review:
        query = r"INSERT INTO REVIEWS (`USER_ID`, `PRODUCT_ID`, `STARS`, `REVIEW`) VALUES (?, ?, ?, ?) RETURNING *"
        cursor = connection.cursor()
        cursor.execute(query, (user_id, product_id, stars, review))
        data = cursor.fetchone()
        connection.commit()

        return cls(connection, **data)

    @classmethod
    def from_user(cls, connection: sqlite3.Connection, *, user_id: int) -> list[Review]:
        query = r"SELECT * FROM REVIEWS WHERE USER_ID = ?"
        cursor = connection.cursor()
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()

        return [cls(connection, **row) for row in rows]

    @classmethod
    def from_product(
        cls, connection: sqlite3.Connection, *, product_id: int
    ) -> list[Review]:
        query = r"SELECT * FROM REVIEWS WHERE PRODUCT_ID = ?"
        cursor = connection.cursor()
        cursor.execute(query, (product_id,))
        rows = cursor.fetchall()

        return [cls(connection, **row) for row in rows]

    def delete(self) -> None:
        query = r"DELETE FROM REVIEWS WHERE `USER_ID` = ? AND `PRODUCT_ID` = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.user_id, self.product_id))
        self.__conn.commit()


class Product:
    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        id: int,
        unique_id: str,
        name: str,
        price: float,
        description: str,
        stock: int,
        size: str,
    ):
        self.__conn = connection
        self.id = id
        self.unique_id = unique_id
        self.name = name
        self.price = price
        self.description = description
        self.images = get_product_pictures(unique_id)
        self.stock = stock
        self.size = size
        self.size_name = size_names[size]

    @property
    def reviews(self) -> list[Review]:
        return Review.from_product(self.__conn, product_id=self.id)

    @property
    def average_rating(self) -> float:
        reviews = self.reviews
        if not reviews:
            return 0.0

        return sum(review.stars for review in reviews) / self.total_reviews

    @property
    def total_reviews(self) -> int:
        return len(self.reviews)

    def add_review(self, *, user_id: int, stars: VALID_STARS, review: str):
        return Review.create(
            self.__conn, user_id=user_id, product_id=self.id, stars=stars, review=review
        )

    def del_review(self, *, user_id: int) -> None:
        query = r"DELETE FROM REVIEWS WHERE `USER_ID` = ? AND `PRODUCT_ID` = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (user_id, self.id))
        self.__conn.commit()

    def is_available(self, count: QUANTITY = 1, *, size: str) -> bool:
        if self.stock == -1:
            return True

        query = r"SELECT STOCK FROM PRODUCTS WHERE UNIQUE_ID = ? AND STOCK >= ? AND SIZE = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.unique_id, count, size))
        stock = cursor.fetchone()

        if stock is None:
            return False

        stock = stock[0]
        return stock >= count and stock > 0

    def use(self, count: QUANTITY = 1, *, size: str) -> None:
        if self.stock == -1:
            return

        query = r"UPDATE PRODUCTS SET STOCK = STOCK - ? WHERE UNIQUE_ID = ? AND STOCK >= ? AND SIZE = ?"
        cursor = self.__conn.cursor()

        cursor.execute(query, (count, self.id, count, size))
        updated = cursor.rowcount

        if updated == 0:
            error = "Product is not available."
            raise ValueError(error)

        self.__conn.commit()

    def release(self, count: QUANTITY = 1, *, size: str) -> None:
        if self.stock == -1:
            return

        query = r"UPDATE PRODUCTS SET STOCK = STOCK + ? WHERE ID = ? AND SIZE = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (count, self.id, size))
        self.__conn.commit()

    @classmethod
    def create(
        cls,
        connection: sqlite3.Connection,
        *,
        unique_id: str,
        name: str,
        price: float,
        description: str,
        stock: int = 0,
        size: str,
    ) -> Product:
        cursor = connection.cursor()

        query = r"""
            INSERT INTO PRODUCTS (UNIQUE_ID, NAME, PRICE, DESCRIPTION, STOCK, SIZE) VALUES (?, ?, ?, ?, ?, ?)
            RETURNING *
        """
        result = cursor.execute(
            query, (unique_id, name, price, description, stock, size)
        )
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
    def from_unique_id(
        cls, connection: sqlite3.Connection, unique_id: str, *, size: str = ""
    ) -> list[Product]:
        cursor = connection.cursor()

        query = r"SELECT * FROM PRODUCTS WHERE UNIQUE_ID = ?"
        if size:
            query += " AND SIZE = ?"
            cursor.execute(query, (unique_id, size))
        else:
            cursor.execute(query, (unique_id,))

        ls = []

        while row := cursor.fetchone():
            ls.append(cls(connection, **row))

        return ls

    @classmethod
    def all(cls, connection: sqlite3.Connection, *, admin: bool = False) -> list[Product]:
        query = r"""
            SELECT *
            FROM PRODUCTS
            WHERE ROWID IN (
                SELECT MIN(ROWID)
                FROM PRODUCTS
                GROUP BY UNIQUE_ID
            )
        """
        if admin:
            query = "SELECT * FROM PRODUCTS"

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

    def get_product(self, product_id: PRODUCT_ID) -> Product:
        return Product.from_id(self.__conn, product_id)

    def add_product(self, *, product: Product, quantity: QUANTITY | None = 1) -> None:
        quantity = quantity or 1
        if not product.is_available(quantity, size=product.size):
            error = "Product is not available."
            raise ValueError(error)

        query = "INSERT INTO CARTS (USER_ID, PRODUCT_ID, QUANTITY) VALUES (?, ?, ?) ON CONFLICT(USER_ID, PRODUCT_ID) DO UPDATE SET QUANTITY = QUANTITY + ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.user_id, product.id, quantity, quantity))
        self.__conn.commit()

        product.use(quantity, size=product.size)

    def remove_product(self, *, product: Product, _: QUANTITY = 1) -> None:
        query = (
            r"DELETE FROM CARTS WHERE USER_ID = ? AND PRODUCT_ID = ? RETURNING QUANTITY"
        )
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.user_id, product.id))
        row = cursor.fetchone()
        self.__conn.commit()

        product.release(int(row[0]), size=product.size)

    def total(self) -> float:
        query = r"""
            SELECT SUM(QUANTITY * (SELECT PRICE FROM PRODUCTS WHERE ID = PRODUCT_ID))
            FROM CARTS
            WHERE USER_ID = ?
        """
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.user_id,))
        total = cursor.fetchone()
        return float(total[0] or 0.0)

    @property
    def count(self) -> int:
        query = r"SELECT SUM(DISTINCT PRODUCT_ID) FROM CARTS WHERE USER_ID = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.user_id,))
        count = cursor.fetchone()
        return int(count[0] or 0)

    def update_to_database(self, *, gift_card: GiftCard | None = None) -> None:
        query = r"""
            INSERT INTO ORDERS (USER_ID, PRODUCT_ID, QUANTITY, TOTAL_PRICE)
                SELECT USER_ID, PRODUCT_ID, QUANTITY, ((QUANTITY * (SELECT PRICE FROM PRODUCTS WHERE ID = PRODUCT_ID)) - ?)
                FROM CARTS
                WHERE USER_ID = ?
        """

        cursor = self.__conn.cursor()

        try:
            cursor.execute(r"BEGIN TRANSACTION")
            cursor.execute(
                query,
                (
                    gift_card.price if gift_card else 0,
                    self.user_id,
                ),
            )
            cursor.execute(r"DELETE FROM CARTS WHERE USER_ID = ?", (self.user_id,))
            cursor.execute(r"COMMIT")
        except sqlite3.Error as e:
            cursor.execute(r"ROLLBACK")
            raise e

    def clear(self, *, product: Product | None = None) -> None:
        query = r"DELETE FROM CARTS WHERE USER_ID = ?"
        args = (self.user_id,)

        if product:
            query += " AND PRODUCT_ID = ?"
            args += (product.id,)

        cursor = self.__conn.cursor()
        cursor.execute(query, args)
        self.__conn.commit()

    def products(self) -> list[Product]:
        query = r"SELECT PRODUCT_ID, QUANTITY FROM CARTS WHERE USER_ID = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.user_id,))

        products = []

        while row := cursor.fetchone():
            product = Product.from_id(self.__conn, row[0])
            product.stock = row[1]
            products.append(product)

        return products


class GiftCard:
    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        id: int,
        price: float,
        user_id: int,
        code: str,
        used: int,
        created_at: str | None,
        used_at: str | None,
    ):
        self.conn = connection
        self.id = id
        self.price = int(price)
        self.user_id = user_id
        self.__code = code
        self.used = bool(int(used))
        self.created_at = created_at
        self.used_at = used_at

    @property
    def code(self) -> str:
        return self.__code

    @property
    def user(self) -> User:
        from .user import User

        return User.from_id(self.conn, self.user_id)

    @classmethod
    def create(cls, conn: sqlite3.Connection, *, user: User, amount: int) -> GiftCard:
        cursor = conn.cursor()

        query = r"""
            INSERT INTO GIFT_CARDS (USER_ID, PRICE, CODE) VALUES (?, ?, ?) RETURNING *
        """
        cursor.execute(query, (user.id, amount, generate_gift_card_code()))
        data = cursor.fetchone()
        conn.commit()

        return cls(conn, **data)

    def use(self) -> None:
        if not self.is_valid:
            error = "Gift card is already used."
            raise ValueError(error)

        query = (
            r"UPDATE GIFT_CARDS SET USED = 1, USED_AT = CURRENT_TIMESTAMP WHERE ID = ?"
        )
        cursor = self.conn.cursor()
        cursor.execute(query, (self.id,))
        self.conn.commit()

    @property
    def is_valid(self) -> bool:
        return not self.used

    @classmethod
    def exists(cls, conn: sqlite3.Connection, *, code: str) -> GiftCard:
        query = r"SELECT * FROM GIFT_CARDS WHERE CODE = ?"
        cursor = conn.cursor()
        cursor.execute(query, (code,))

        if row := cursor.fetchone():
            return cls(conn, **row)

        error = "Gift card not found."
        raise ValueError(error) from None

    @classmethod
    def from_code(cls, conn: sqlite3.Connection, code: str) -> GiftCard | None:
        try:
            return cls.exists(conn, code=code)
        except ValueError:
            return None
