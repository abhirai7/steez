from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Literal

from fuzzywuzzy.fuzz import partial_ratio

from .utils import SQLITE_OLD, generate_gift_card_code, get_product_pictures, size_names

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
        if SQLITE_OLD:
            query = r"INSERT INTO REVIEWS (`USER_ID`, `PRODUCT_ID`, `STARS`, `REVIEW`) VALUES (?, ?, ?, ?)"
        else:
            query = r"INSERT INTO REVIEWS (`USER_ID`, `PRODUCT_ID`, `STARS`, `REVIEW`) VALUES (?, ?, ?, ?) RETURNING *"
        cursor = connection.cursor()
        result = cursor.execute(query, (user_id, product_id, stars, review))

        if SQLITE_OLD:
            result = cursor.execute(
                r"SELECT * FROM REVIEWS WHERE ROWID = ?", (cursor.lastrowid,)
            )

        data = result.fetchone()
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


class Category:
    def __init__(
        self, connection: sqlite3.Connection, *, id: int, name: str, description: str
    ):
        self.__conn = connection
        self.id = id
        self.name = name
        self.description = description

    def __hash__(self) -> int:
        return hash(self.id)

    def delete(self) -> None:
        query = r"DELETE FROM CATEGORIES WHERE ID = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.id,))
        self.__conn.commit()

    @classmethod
    def create(
        cls, connection: sqlite3.Connection, *, name: str, description: str
    ) -> Category:
        cursor = connection.cursor()

        if SQLITE_OLD:
            query = r"INSERT INTO CATEGORIES (NAME, DESCRIPTION) VALUES (?, ?)"
            cursor.execute(query, (name, description))
            result = cursor.execute(
                r"SELECT * FROM CATEGORIES WHERE ROWID = ?", (cursor.lastrowid,)
            )
        else:
            query = (
                r"INSERT INTO CATEGORIES (NAME, DESCRIPTION) VALUES (?, ?) RETURNING *"
            )
            result = cursor.execute(query, (name, description))

        data = result.fetchone()
        connection.commit()

        return cls(connection, **data)

    @classmethod
    def from_id(cls, connection: sqlite3.Connection, category_id: int) -> Category:
        query = r"SELECT * FROM CATEGORIES WHERE ID = ?"
        cursor = connection.cursor()
        cursor.execute(query, (category_id,))
        row = cursor.fetchone()
        if row is None:
            error = "Category not found."
            raise ValueError(error) from None
        return cls(connection, **row)

    @classmethod
    def from_name(cls, connection: sqlite3.Connection, name: str) -> Category:
        query = r"SELECT * FROM CATEGORIES WHERE NAME = ?"
        cursor = connection.cursor()
        cursor.execute(query, (name,))
        row = cursor.fetchone()
        if row is None:
            error = "Category not found."
            raise ValueError(error) from None
        return cls(connection, **row)

    @classmethod
    def all(cls, connection: sqlite3.Connection) -> list[Category]:
        query = r"SELECT * FROM CATEGORIES"
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [cls(connection, **row) for row in rows]

    @staticmethod
    def total_count(connection: sqlite3.Connection) -> int:
        query = r"SELECT COUNT(*) FROM CATEGORIES"
        cursor = connection.cursor()
        cursor.execute(query)
        count = cursor.fetchone()
        return int(count[0])

    def json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

    def __repr__(self) -> str:
        return f"<Category name={self.name} description={self.description}>"


class Product:
    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        id: int,
        unique_id: str,
        name: str,
        price: float,
        display_price: float,
        description: str,
        stock: int,
        size: str,
        category: int,
        keywords: str = "",
        created_at: str = "",
    ):
        self.__conn = connection
        self.id = id
        self.unique_id = unique_id
        self.name = name
        self.price = price
        self.display_price = display_price
        self.description = description
        self.images = get_product_pictures(unique_id)
        self.stock = stock
        self.size = size
        self.size_name = size_names[size]
        self.category = Category.from_id(connection, category)
        self.keywords = [keyword.strip() for keyword in keywords.split(";")]

        self._available_sizes = []

    def update(self) -> None:
        query = r"""
            UPDATE PRODUCTS
            SET NAME = ?, PRICE = ?, DISPLAY_PRICE = ?, DESCRIPTION = ?, STOCK = ?, SIZE = ?, CATEGORY = ?, KEYWORDS = ?
            WHERE ID = ?
        """
        cursor = self.__conn.cursor()
        cursor.execute(
            query,
            (
                self.name,
                self.price,
                self.display_price,
                self.description,
                self.stock,
                self.size,
                self.category.id,
                ";".join(self.keywords),
                self.id,
            ),
        )

    @property
    def available_sizes(self) -> list[str]:
        if self._available_sizes:
            return self._available_sizes

        query = r"SELECT SIZE FROM PRODUCTS WHERE UNIQUE_ID = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.unique_id,))
        ls = []

        while row := cursor.fetchone():
            ls.append(row[0])

        self._available_sizes = ls
        return ls

    @property
    def reviews(self) -> list[Review]:
        return Review.from_product(self.__conn, product_id=self.id)

    @property
    def average_rating(self) -> float:
        if reviews := self.reviews:
            return sum(review.stars for review in reviews) / self.total_reviews

        return 0.0

    @property
    def total_reviews(self) -> int:
        return len(self.reviews)

    def add_review(self, *, user_id: int, stars: VALID_STARS, review: str):
        return Review.create(
            self.__conn, user_id=user_id, product_id=self.id, stars=stars, review=review
        )

    def delete_review(self, *, user_id: int) -> None:
        query = r"DELETE FROM REVIEWS WHERE `USER_ID` = ? AND `PRODUCT_ID` = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (user_id, self.id))
        self.__conn.commit()

    def is_available(self, count: QUANTITY = 1) -> bool:
        if self.stock == -1:
            return True

        query = r"SELECT STOCK FROM PRODUCTS WHERE UNIQUE_ID = ? AND STOCK >= ? AND SIZE = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.unique_id, count, self.size))
        stock = cursor.fetchone()

        if stock is None:
            return False

        stock = stock[0]
        return stock >= count and stock > 0

    def use(self, count: QUANTITY = 1) -> None:
        if self.stock == -1:
            return

        query = r"UPDATE PRODUCTS SET STOCK = STOCK - ? WHERE UNIQUE_ID = ? AND STOCK >= ? AND SIZE = ?"
        cursor = self.__conn.cursor()

        cursor.execute(query, (count, self.unique_id, count, self.size))
        updated = cursor.rowcount

        if updated == 0:
            error = "Product is not available."
            raise ValueError(error)

        self.__conn.commit()

    def release(self, count: QUANTITY = 1) -> None:
        if self.stock == -1:
            return

        query = r"UPDATE PRODUCTS SET STOCK = STOCK + ? WHERE ID = ? AND SIZE = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (count, self.id, self.size))
        self.__conn.commit()

    @classmethod
    def create(
        cls,
        connection: sqlite3.Connection,
        *,
        unique_id: str,
        name: str,
        price: float,
        display_price: float,
        description: str,
        category: int,
        stock: int = 0,
        size: str,
        keywords: str = "",
    ) -> Product:
        cursor = connection.cursor()

        if SQLITE_OLD:
            query = r"""
                INSERT INTO PRODUCTS (UNIQUE_ID, NAME, PRICE, DESCRIPTION, STOCK, SIZE, DISPLAY_PRICE, CATEGORY, KEYWORDS)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(
                query,
                (
                    unique_id,
                    name,
                    price,
                    description,
                    stock,
                    size,
                    display_price,
                    category,
                    keywords,
                ),
            )
            result = cursor.execute(
                r"SELECT * FROM PRODUCTS WHERE ROWID = ?", (cursor.lastrowid,)
            )
        else:
            query = r"""
                INSERT INTO PRODUCTS (UNIQUE_ID, NAME, PRICE, DESCRIPTION, STOCK, SIZE, DISPLAY_PRICE, CATEGORY, KEYWORDS)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING *
            """
            result = cursor.execute(
                query,
                (
                    unique_id,
                    name,
                    price,
                    description,
                    stock,
                    size,
                    display_price,
                    category,
                    keywords,
                ),
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
    def from_size(cls, connection: sqlite3.Connection, *, id: int, size: str):
        query = r"SELECT * FROM PRODUCTS WHERE UNIQUE_ID = (SELECT UNIQUE_ID FROM PRODUCTS WHERE ID = ?) AND SIZE = ?"
        cursor = connection.cursor()
        cursor.execute(query, (id, size))
        row = cursor.fetchone()
        if row is None:
            error = "Product not found."
            raise ValueError(error) from None
        return cls(connection, **row)

    @classmethod
    def all(
        cls,
        connection: sqlite3.Connection,
        *,
        admin: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Product]:
        params = (limit, offset) if limit is not None else ()
        if limit is None:
            query = r"""
                SELECT * FROM PRODUCTS WHERE ROWID IN (SELECT MIN(ROWID) FROM PRODUCTS GROUP BY UNIQUE_ID) AND STOCK > 0
            """
        else:
            query = r"""
                SELECT * FROM PRODUCTS WHERE ROWID IN (SELECT MIN(ROWID) FROM PRODUCTS GROUP BY UNIQUE_ID) AND STOCK > 0 LIMIT ? OFFSET ?
            """
        if admin:
            if limit is None:
                query = r"SELECT * FROM PRODUCTS"
            else:
                query = r"SELECT * FROM PRODUCTS LIMIT ? OFFSET ?"

        cursor = connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [cls(connection, **row) for row in rows]

    @staticmethod
    def total_count(connection: sqlite3.Connection) -> int:
        query = r"SELECT COUNT(*) FROM PRODUCTS"
        cursor = connection.cursor()
        cursor.execute(query)
        count = cursor.fetchone()
        return int(count[0])

    @classmethod
    def search(cls, connection: sqlite3.Connection, query: str) -> list[Product]:
        all_products = cls.all(connection)

        return sorted(
            all_products,
            key=lambda product: partial_ratio(
                query,
                f"{product.name} {product.description} {' '.join(product.keywords)}",
            ),
            reverse=True,
        )

    def json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "stock": self.stock,
        }

    def __repr__(self) -> str:
        return f"<Product name={self.name} price={self.price} stock={self.stock} unique_id={self.unique_id} size={self.size_name}>"

    @staticmethod
    def categorise_products(products: list[Product]) -> dict[Category, list[Product]]:
        categories: dict[Category, list[Product]] = {}
        for product in products:
            if product.category not in categories:
                categories[product.category] = []

            categories[product.category].append(product)

        return categories


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
        if not product.is_available(quantity):
            error = "Product is not available."
            raise ValueError(error)

        query = r"INSERT INTO CARTS (USER_ID, PRODUCT_ID, QUANTITY) VALUES (?, ?, ?) ON CONFLICT(USER_ID, PRODUCT_ID) DO UPDATE SET QUANTITY = QUANTITY + ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.user_id, product.id, quantity, quantity))
        self.__conn.commit()

        product.use(quantity)

    def remove_product(self, *, product: Product, _: QUANTITY = 1) -> None:
        query = (
            r"DELETE FROM CARTS WHERE USER_ID = ? AND PRODUCT_ID = ? RETURNING QUANTITY"
        )
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.user_id, product.id))
        row = cursor.fetchone()
        self.__conn.commit()

        product.release(int(row[0]))

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
        query = r"SELECT SUM(QUANTITY) FROM CARTS WHERE USER_ID = ?"
        cursor = self.__conn.cursor()
        cursor.execute(query, (self.user_id,))
        count = cursor.fetchone()
        return int(count[0] or 0)

    def update_to_database(self, *, gift_card: GiftCard | None = None) -> None:
        query = r"""
            INSERT INTO ORDERS (USER_ID, PRODUCT_ID, QUANTITY, TOTAL_PRICE)
                SELECT 
                    USER_ID, PRODUCT_ID, QUANTITY, MAX(((QUANTITY * (SELECT PRICE FROM PRODUCTS WHERE ID = PRODUCT_ID)) - ?), 1)
                FROM CARTS
                WHERE USER_ID = ?
        """

        cursor = self.__conn.cursor()

        try:
            cursor.execute(
                query,
                (
                    gift_card.price if (gift_card and gift_card.is_valid) else 0,
                    self.user_id,
                ),
            )
            if gift_card:
                gift_card.use()

            cursor.execute(r"DELETE FROM CARTS WHERE USER_ID = ?", (self.user_id,))
            self.__conn.commit()
        except sqlite3.Error as e:
            self.__conn.commit()
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
        used: int | str,
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

    @staticmethod
    def admin_create(conn: sqlite3.Connection, *, user: User, amount: int) -> GiftCard:
        assert user.is_admin, "Only admins can create gift cards."

        cursor = conn.cursor()

        query = r"""
            INSERT INTO GIFT_CARDS (USER_ID, PRICE, CODE) VALUES (?, ?, ?) RETURNING *
        """
        cursor.execute(query, (user.id, amount, generate_gift_card_code()))
        data = cursor.fetchone()
        conn.commit()

        return GiftCard(conn, **data)

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

    @classmethod
    def all(cls, conn: sqlite3.Connection) -> list[GiftCard]:
        query = r"SELECT * FROM GIFT_CARDS"
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [cls(conn, **row) for row in rows]
