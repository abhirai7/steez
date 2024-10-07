from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Literal

import arrow
from fuzzywuzzy.fuzz import partial_ratio

from .utils import SQLITE_OLD, generate_gift_card_code, get_product_pictures, size_names

VALID_STARS = Literal[1, 2, 3, 4, 5]
PRODUCT_ID = int
QUANTITY = int
from flask_sqlalchemy import SQLAlchemy

if TYPE_CHECKING:
    from .user import User


class Review:
    def __init__(
        self,
        db: SQLAlchemy,
        *,
        id: int,
        user_id: int,
        product_id: int,
        review: str | None = None,
        stars: VALID_STARS,
        created_at: str | None = None,
    ):
        self.__db = db
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.stars = stars
        self.review = review
        self.created_at = arrow.get(created_at) if created_at else None

    @property
    def user(self) -> User:
        from .user import User

        return User.from_id(self.__db, self.user_id)

    @property
    def product(self) -> Product:
        return Product.from_id(self.__db, self.product_id)

    @classmethod
    def create(
        cls,
        db: SQLAlchemy,
        *,
        user_id: int,
        product_id: int,
        review: str,
        stars: VALID_STARS,
    ) -> Review:
        from src.server.models import Reviews

        r = Reviews(USER_ID=user_id, PRODUCT_ID=product_id, REVIEW=review, STARS=stars)
        db.session.add(r)
        db.session.commit()

        return cls(db, **r.__dict__)

    @classmethod
    def from_user(cls, db: SQLAlchemy, *, user_id: int) -> list[Review]:
        from src.server.models import Reviews

        reviews = Reviews.query.filter_by(USER_ID=user_id).all()

        return [cls(db, **review.__dict__) for review in reviews]

    @classmethod
    def from_product(cls, db: SQLAlchemy, *, product_id: int) -> list[Review]:
        from src.server.models import Reviews

        reviews = Reviews.query.filter_by(PRODUCT_ID=product_id).all()

        return [cls(db, **review.__dict__) for review in reviews]

    def delete(self) -> None:
        from src.server.models import Reviews

        self.__db.session.delete(Reviews.query.get(self.id))
        self.__db.session.commit()


class Category:
    def __init__(self, db: SQLAlchemy, *, id: int, name: str, description: str):
        self.__db = db
        self.id = id
        self.name = name
        self.description = description

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Category) -> bool:
        return self.id == other.id

    def delete(self) -> None:
        from src.server.models import Categories

        self.__db.session.delete(Categories.query.get(self.id))
        self.__db.session.commit()

    @classmethod
    def create(cls, db: SQLAlchemy, *, name: str, description: str) -> Category:
        from src.server.models import Categories

        category = Categories(NAME=name, DESCRIPTION=description)
        db.session.add(category)
        db.session.commit()

        return cls(db, **category.__dict__)

    @classmethod
    def from_id(cls, db: SQLAlchemy, category_id: int) -> Category:
        from src.server.models import Categories

        category = Categories.query.get(category_id)
        if category is None:
            error = "Category not found."
            raise ValueError(error) from None
        
        return cls(db, **category.__dict__)

    @classmethod
    def from_name(cls, db: SQLAlchemy, name: str) -> Category:
        from src.server.models import Categories

        category = Categories.query.filter_by(NAME=name).first()

        if category is None:
            error = "Category not found."
            raise ValueError(error) from None
        
        return cls(db, **category.__dict__)

    @classmethod
    def all(cls, db: SQLAlchemy) -> list[Category]:
        from src.server.models import Categories

        all_categories = Categories.query.all()
        return [cls(db, **category.__dict__) for category in all_categories]

    @staticmethod
    def total_count(_: SQLAlchemy) -> int:
        from src.server.models import Categories

        return Categories.query.count()

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
        db: SQLAlchemy,
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
        self.__db = db
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
        self.category = Category.from_id(db, category)
        self.keywords = [keyword.strip() for keyword in keywords.split(";")]

        self._available_sizes = []
        self.created_at = arrow.get(created_at)

    def update(self) -> None:
        from src.server.models import Products

        product = Products.query.get(self.id)
        product.NAME = self.name
        product.PRICE = self.price
        product.DISPLAY_PRICE = self.display_price
        product.DESCRIPTION = self.description
        product.STOCK = self.stock
        product.SIZE = self.size
        product.CATEGORY = self.category.id
        product.KEYWORDS = ";".join(self.keywords)
        
        self.__db.session.commit()

    def similar_products(self) -> list[Product]:
        keywords_query = " OR ".join([f"KEYWORDS LIKE '%{keyword}%'" for keyword in self.keywords])

        query = f"SELECT * FROM PRODUCTS WHERE ID != ? AND ({keywords_query}) AND ROWID IN (SELECT MIN(ROWID) FROM PRODUCTS GROUP BY UNIQUE_ID) ORDER BY CREATED_AT DESC LIMIT 3"
        cursor = self.__db.cursor()
        cursor.execute(query, (self.id,))

        products = []

        while row := cursor.fetchone():
            products.append(Product(self.__db, **row))

        return products

    @property
    def available_sizes(self) -> list[str]:
        if self._available_sizes:
            return self._available_sizes

        query = r"SELECT SIZE FROM PRODUCTS WHERE UNIQUE_ID = ?"
        cursor = self.__db.cursor()
        cursor.execute(query, (self.unique_id,))
        ls = []

        while row := cursor.fetchone():
            ls.append(row[0])

        self._available_sizes = ls
        return ls

    @property
    def reviews(self) -> list[Review]:
        return Review.from_product(self.__db, product_id=self.id)

    @property
    def categorised_reviews(self) -> dict[VALID_STARS, list[Review]]:
        reviews = self.reviews
        return {i: [review for review in reviews if review.stars == i] for i in range(1, 6)}  # type: ignore

    @property
    def average_rating(self) -> float:
        if reviews := self.reviews:
            avg = sum(review.stars for review in reviews) / self.total_reviews
            return round(avg, 2)

        return 0.0

    @property
    def total_reviews(self) -> int:
        return len(self.reviews)

    @property
    def discount(self) -> int:
        return int((abs(self.price - self.display_price) / self.price) * 100)

    def add_review(self, *, user_id: int, stars: VALID_STARS, review: str):
        return Review.create(self.__db, user_id=user_id, product_id=self.id, stars=stars, review=review)

    def delete_review(self, *, user_id: int) -> None:
        query = r"DELETE FROM REVIEWS WHERE `USER_ID` = ? AND `PRODUCT_ID` = ?"
        cursor = self.__db.cursor()
        cursor.execute(query, (user_id, self.id))
        self.__db.commit()

    def is_available(self, count: QUANTITY = 1) -> bool:
        if self.stock == -1:
            return True

        query = r"SELECT STOCK FROM PRODUCTS WHERE UNIQUE_ID = ? AND STOCK >= ? AND SIZE = ?"
        cursor = self.__db.cursor()
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
        cursor = self.__db.cursor()

        cursor.execute(query, (count, self.unique_id, count, self.size))
        updated = cursor.rowcount

        if updated == 0:
            error = "Product is not available."
            raise ValueError(error)

        self.__db.commit()

    def release(self, count: QUANTITY = 1) -> None:
        if self.stock == -1:
            return

        query = r"UPDATE PRODUCTS SET STOCK = STOCK + ? WHERE ID = ? AND SIZE = ?"
        cursor = self.__db.cursor()
        cursor.execute(query, (count, self.id, self.size))
        self.__db.commit()

    @classmethod
    def create(
        cls,
        db: SQLAlchemy,
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
            result = cursor.execute(r"SELECT * FROM PRODUCTS WHERE ROWID = ?", (cursor.lastrowid,))
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
    def from_id(cls, db: SQLAlchemy, product_id: PRODUCT_ID) -> Product:
        query = r"SELECT * FROM PRODUCTS WHERE ID = ?"
        cursor = connection.cursor()
        cursor.execute(query, (product_id,))
        row = cursor.fetchone()
        if row is None:
            error = "Product not found."
            raise ValueError(error) from None
        return cls(connection, **row)

    @classmethod
    def from_unique_id(cls, db: SQLAlchemy, unique_id: str, *, size: str = "") -> list[Product]:
        cursor = connection.cursor()

        query = r"SELECT * FROM PRODUCTS WHERE UNIQUE_ID = ? AND ROWID IN (SELECT MIN(ROWID) FROM PRODUCTS GROUP BY UNIQUE_ID)"
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
    def from_size(cls, db: SQLAlchemy, *, id: int, size: str):
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
        db: SQLAlchemy,
        *,
        admin: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Product]:
        params = ()
        query = r"""
            SELECT * FROM PRODUCTS WHERE ROWID IN (SELECT MIN(ROWID) FROM PRODUCTS GROUP BY UNIQUE_ID) AND STOCK > 0
        """
        if admin:
            if limit is None:
                query = r"SELECT * FROM PRODUCTS"
            else:
                params = (limit, offset) if limit is not None else ()
                query = r"SELECT * FROM PRODUCTS LIMIT ? OFFSET ?"

        cursor = connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [cls(connection, **row) for row in rows]

    @staticmethod
    def total_count(db: SQLAlchemy) -> int:
        query = r"SELECT COUNT(*) FROM PRODUCTS"
        cursor = connection.cursor()
        cursor.execute(query)
        count = cursor.fetchone()
        return int(count[0])

    @classmethod
    def search(cls, db: SQLAlchemy, query: str) -> list[Product]:
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
    def categorise_products(products: list[Product], *, limit: int | None = None) -> dict[Category, list[Product]]:
        categories: dict[Category, list[Product]] = {}
        limit = limit or float("inf")  # type: ignore

        for product in products:
            if product.category not in categories:
                categories[product.category] = []

            if len(categories[product.category]) >= limit:  # type: ignore
                continue

            categories[product.category].append(product)

        return categories

    @classmethod
    def get_by_category(cls, conn: sqlite3.Connection, category: Category) -> list[Product]:
        query = r"SELECT * FROM PRODUCTS WHERE CATEGORY = ? AND ROWID IN (SELECT MIN(ROWID) FROM PRODUCTS GROUP BY UNIQUE_ID)"
        cursor = conn.cursor()
        cursor.execute(query, (category.id,))

        products = []

        while row := cursor.fetchone():
            products.append(cls(conn, **row))

        return products


class Cart:
    def __init__(
        self,
        db: SQLAlchemy,
        *,
        user_id: int,
    ):
        self.__db = db
        self.user_id = user_id

    def get_product(self, product_id: PRODUCT_ID) -> Product:
        return Product.from_id(self.__db, product_id)

    def add_product(self, *, product: Product, quantity: QUANTITY | None = 1) -> None:
        quantity = quantity or 1
        if not product.is_available(quantity):
            error = "Product is not available."
            raise ValueError(error)

        query = r"INSERT INTO CARTS (USER_ID, PRODUCT_ID, QUANTITY) VALUES (?, ?, ?) ON CONFLICT(USER_ID, PRODUCT_ID) DO UPDATE SET QUANTITY = QUANTITY + ?"
        cursor = self.__db.cursor()
        cursor.execute(query, (self.user_id, product.id, quantity, quantity))
        self.__db.commit()

        product.use(quantity)

    def remove_product(self, *, product: Product, _: QUANTITY = 1) -> None:
        query = r"DELETE FROM CARTS WHERE USER_ID = ? AND PRODUCT_ID = ? RETURNING QUANTITY"
        cursor = self.__db.cursor()
        cursor.execute(query, (self.user_id, product.id))
        row = cursor.fetchone()
        self.__db.commit()

        product.release(int(row[0]))

    def total(self) -> float:
        query = r"""
            SELECT SUM(QUANTITY * (SELECT PRICE FROM PRODUCTS WHERE ID = PRODUCT_ID))
            FROM CARTS
            WHERE USER_ID = ?
        """
        cursor = self.__db.cursor()
        cursor.execute(query, (self.user_id,))
        total = cursor.fetchone()
        return float(total[0] or 0.0)

    @property
    def count(self) -> int:
        query = r"SELECT SUM(QUANTITY) FROM CARTS WHERE USER_ID = ?"
        cursor = self.__db.cursor()
        cursor.execute(query, (self.user_id,))
        count = cursor.fetchone()
        return int(count[0] or 0)

    def update_to_database(self, *, gift_card: GiftCard | None = None, status: str = "PEND") -> None:
        query = r"""
            INSERT INTO ORDERS (USER_ID, PRODUCT_ID, QUANTITY, TOTAL_PRICE, STATUS) 
                SELECT 
                    USER_ID, PRODUCT_ID, QUANTITY, MAX(((QUANTITY * (SELECT PRICE FROM PRODUCTS WHERE ID = PRODUCT_ID)) - ?), 1), ?
                FROM CARTS
                WHERE USER_ID = ?
        """

        cursor = self.__db.cursor()

        try:
            cursor.execute(
                query,
                (
                    gift_card.price if (gift_card and gift_card.is_valid) else 0,
                    status.upper(),
                    self.user_id,
                ),
            )
            if gift_card:
                gift_card.use()

            cursor.execute(r"DELETE FROM CARTS WHERE USER_ID = ?", (self.user_id,))
            self.__db.commit()
        except sqlite3.Error as e:
            self.__db.commit()
            raise e

    def clear(self, *, product: Product | None = None) -> None:
        query = r"DELETE FROM CARTS WHERE USER_ID = ?"
        args = (self.user_id,)

        if product:
            query += " AND PRODUCT_ID = ?"
            args += (product.id,)

        cursor = self.__db.cursor()
        cursor.execute(query, args)
        self.__db.commit()

    def products(self) -> list[Product]:
        query = r"SELECT PRODUCT_ID, QUANTITY FROM CARTS WHERE USER_ID = ?"
        cursor = self.__db.cursor()
        cursor.execute(query, (self.user_id,))

        products = []

        while row := cursor.fetchone():
            product = Product.from_id(self.__db, row[0])
            product.stock = row[1]
            products.append(product)

        return products


class GiftCard:
    def __init__(
        self,
        db: SQLAlchemy,
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
        self.created_at = arrow.get(created_at) if created_at else None
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

        query = r"UPDATE GIFT_CARDS SET USED = 1, USED_AT = CURRENT_TIMESTAMP WHERE ID = ?"
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
