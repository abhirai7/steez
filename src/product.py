from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import arrow
from flask_sqlalchemy import SQLAlchemy
from fuzzywuzzy.fuzz import partial_ratio
from sqlalchemy import func, insert, literal, literal_column, or_, select

from .utils import generate_gift_card_code, get_product_pictures, size_names

VALID_STARS = Literal[1, 2, 3, 4, 5]
product_id = int
quantity = int

if TYPE_CHECKING:
    from typing_extensions import Self

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
        **_,
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
        from src.server.models import Review as Reviews

        smt = insert(Reviews).values(user_id=user_id, product_id=product_id, REVIEW=review, STARS=stars).returning(literal_column("*"))

        r = db.session.execute(smt).mappings().fetchone()
        db.session.commit()

        return cls(db, **{k.lower(): v for k, v in r.__dict__.items()})

    @classmethod
    def from_user(cls, db: SQLAlchemy, *, user_id: int) -> list[Review]:
        from src.server.models import Review as Reviews

        reviews = Reviews.query.filter_by(user_id=user_id).all()

        return [cls(db, **{k.lower(): v for k, v in review.__dict__.items()}) for review in reviews]

    @classmethod
    def from_product(cls, db: SQLAlchemy, *, product_id: int) -> list[Review]:
        from src.server.models import Review as Reviews

        reviews = Reviews.query.filter_by(product_id=product_id).all()

        return [cls(db, **{k.lower(): v for k, v in review.__dict__.items()}) for review in reviews]

    def delete(self) -> None:
        from src.server.models import Review as Reviews

        self.__db.session.delete(Reviews.query.get(self.id))
        self.__db.session.commit()


class Category:
    def __init__(self, db: SQLAlchemy, *, id: int, name: str, description: str, **_):
        self.__db = db
        self.id = id
        self.name = name
        self.description = description

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Category) -> bool:
        return self.id == other.id

    def delete(self) -> None:
        from src.server.models import Category as Categories

        self.__db.session.delete(Categories.query.get(self.id))
        self.__db.session.commit()

    @classmethod
    def create(cls, db: SQLAlchemy, *, name: str, description: str) -> Category:
        from src.server.models import Category as Categories

        smt = insert(Categories).values(name=name, description=description).returning(literal_column("*"))
        category = db.session.execute(smt).mappings().fetchone()
        db.session.commit()

        assert category, "Category not found."

        return cls(db, **{k.lower(): v for k, v in category.items()})

    @classmethod
    def from_id(cls, db: SQLAlchemy, category_id: int) -> Category:
        from src.server.models import Category as Categories

        category = Categories.query.get(category_id)
        if category is None:
            error = "Category not found."
            raise ValueError(error) from None

        return cls(db, **{k.lower(): v for k, v in category.__dict__.items()})

    @classmethod
    def from_name(cls, db: SQLAlchemy, name: str) -> Category:
        from src.server.models import Category as Categories

        category = Categories.query.filter_by(name=name).first()

        if category is None:
            error = "Category not found."
            raise ValueError(error) from None

        return cls(db, **{k.lower(): v for k, v in category.__dict__.items()})

    @classmethod
    def all(cls, db: SQLAlchemy) -> list[Category]:
        from src.server.models import Category as Categories

        with db.session() as conn:
            all_categories = conn.query(Categories).all()

        return [cls(db, **{k.lower(): v for k, v in category.__dict__.items()}) for category in all_categories]

    @staticmethod
    def total_count(_: SQLAlchemy) -> int:
        from src.server.models import Category as Categories

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
        **_,
    ):
        self.__db: SQLAlchemy = db
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
        from src.server.models import Product as Products

        product = Products.query.get(self.id)

        assert product, "Product not found."

        product.name = self.name
        product.price = self.price
        product.display_price = self.display_price
        product.description = self.description
        product.stock = self.stock
        product.size = self.size
        product.category = self.category.id
        product.keywords = ";".join(self.keywords)

        self.__db.session.commit()

    def similar_products(self) -> list[Product]:
        from src.server.models import Product as Products

        query = or_(*[Products.keywords.like(f"%{keyword}%") for keyword in self.keywords])

        products_query = (
            self.__db.session.query(Products)
            .filter(Products.id != self.id)
            .filter(query)
            .distinct(Products.unique_id)
            .order_by(Products.created_at.desc())
            .limit(3)
        )

        with self.__db.session() as conn:
            ls = []

            for row in conn.execute(products_query).mappings():
                ls.append(Product(self.__db, **row))

            return ls

    @property
    def available_sizes(self) -> list[str]:
        if self._available_sizes:
            return self._available_sizes

        from src.server.models import Product as Products

        sizes_query = self.__db.session.query(Products.size).filter(Products.unique_id == self.unique_id)

        with self.__db.session() as conn:
            self._available_sizes = [size for (size,) in conn.execute(sizes_query).all()]

        return self._available_sizes

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
        from src.server.models import Review as Reviews

        Reviews.query.filter_by(user_id=user_id, product_id=self.id).delete()

        self.__db.session.commit()

    def is_available(self, count: quantity = 1) -> bool:
        if self.stock == -1:
            return True

        from src.server.models import Product as Products

        stock: int | None = (
            self.__db.session.query(Products.stock).filter(Products.unique_id == self.unique_id, Products.size == self.size).scalar()
        )

        if stock is None:
            return False

        return stock >= count and stock > 0

    def use(self, count: quantity = 1) -> None:
        if self.stock == -1:
            return

        from src.server.models import Product as Products

        updated = Products.query.filter(
            Products.unique_id == self.unique_id,
            Products.size == self.size,
            Products.stock >= count,
        ).update({Products.stock: Products.stock - count})

        if not updated:
            error = "Product not available."
            raise ValueError(error)

        self.__db.session.commit()

    def release(self, count: quantity = 1) -> None:
        if self.stock == -1:
            return

        from src.server.models import Product as Products

        Products.query.filter(
            Products.unique_id == self.unique_id,
            Products.size == self.size,
        ).update({Products.stock: Products.stock + count})

        self.__db.session.commit()

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
        from src.server.models import Product as Products

        smt = (
            insert(Products)
            .values(
                unique_id=unique_id,
                name=name,
                price=price,
                display_price=display_price,
                description=description,
                stock=stock,
                size=size,
                category=category,
                keywords=keywords,
            )
            .returning(literal_column("*"))
        )

        product = db.session.execute(smt).mappings().fetchone()
        if product is None:
            error = "Product not found."
            raise ValueError(error) from None

        db.session.commit()
        return cls(db, **{k.lower(): v for k, v in product.items()})

    @classmethod
    def from_id(cls, db: SQLAlchemy, product_id: product_id) -> Product:
        from src.server.models import Product as Products

        product = Products.query.get(product_id)
        if product is None:
            error = "Product not found."
            raise ValueError(error) from None

        return cls(db, **{k.lower(): v for k, v in product.__dict__.items()})

    @classmethod
    def from_unique_id(cls, db: SQLAlchemy, unique_id: str, *, size: str = "") -> list[Product]:
        from src.server.models import Product as Products

        query = Products.query.filter(Products.unique_id == unique_id)

        if size:
            query = query.filter(Products.size == size)

        products = query.all()

        return [cls(db, **{k.lower(): v for k, v in product.__dict__.items()}) for product in products]

    @classmethod
    def from_size(cls, db: SQLAlchemy, *, id: int, size: str):
        from src.server.models import Product as Products

        _product = Products.query.get(id)
        assert _product, "Product not found."

        product = Products.query.filter(Products.unique_id == _product.unique_id, Products.size == size).first()

        if not product:
            error = "Product not found."
            raise ValueError(error) from None

        return cls(db, **{k.lower(): v for k, v in product.__dict__.items()})

    @classmethod
    def all(
        cls,
        db: SQLAlchemy,
        *,
        admin: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Product]:
        from src.server.models import Product as Products

        query = Products.query.filter(Products.stock > 0).group_by(Products.unique_id)

        if admin:
            query = Products.query

        query = query.order_by(Products.created_at.desc()).limit(limit).offset(offset)
        products = query.all()

        return [cls(db, **{k.lower(): v for k, v in product.__dict__.items()}) for product in products]

    @staticmethod
    def total_count(db: SQLAlchemy) -> int:
        from src.server.models import Product as Products

        return Products.query.count()

    @classmethod
    def search(cls, db: SQLAlchemy, query: str) -> list[Product]:
        all_products = cls.all(db)

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
    def get_by_category(cls, db: SQLAlchemy, category: Category) -> list[Self]:
        from src.server.models import Product as Products

        products = Products.query.filter(Products.category == category.id).distinct(Products.unique_id).all()

        return [cls(db, **{k.lower(): v for k, v in product.__dict__.items()}) for product in products]


class Cart:
    def __init__(
        self,
        db: SQLAlchemy,
        *,
        user_id: int,
    ):
        self.__db = db
        self.user_id = user_id

    def get_product(self, product_id: product_id) -> Product:
        return Product.from_id(self.__db, product_id)

    def add_product(self, *, product: Product, quantity: quantity | None = 1) -> None:
        from src.server.models import Cart as Carts

        quantity = quantity or 1
        if not product.is_available(quantity):
            error = "Product is not available."
            raise ValueError(error)

        cart_item = Carts.query.filter_by(user_id=self.user_id, product_id=product.id).first()

        if cart_item:
            cart_item.quantity += quantity
        else:
            smt = insert(Carts).values(user_id=self.user_id, product_id=product.id, quantity=quantity)
            self.__db.session.execute(smt)

        self.__db.session.commit()

    def remove_product(self, *, product: Product, _: quantity = 1) -> None:
        from src.server.models import Cart as Carts

        cart_item = Carts.query.filter_by(user_id=self.user_id, product_id=product.id).first()

        if cart_item:
            quantity_to_release = cart_item.quantity

            self.__db.session.delete(cart_item)
            self.__db.session.commit()

            product.release(quantity_to_release)

    def total(self) -> float:
        from src.server.models import Cart as Carts
        from src.server.models import Product as Products

        total = (
            self.__db.session.query(func.sum(Carts.quantity * Products.price))
            .join(Products, Carts.product_id == Products.id)
            .filter(Carts.user_id == self.user_id)
            .scalar()
        )

        return float(total or 0.0)

    @property
    def count(self) -> int:
        from src.server.models import Cart as Carts

        count = self.__db.session.query(func.sum(Carts.quantity)).filter(Carts.user_id == self.user_id).scalar()

        return int(count or 0)

    def update_to_database(self, *, gift_card: GiftCard | None = None, status: str = "PEND") -> None:
        from src.server.models import Cart as Carts
        from src.server.models import Order as Orders
        from src.server.models import Product as Products

        total_price_query = (
            self.__db.session.query(
                func.max((Carts.quantity * Products.price) - (gift_card.price if gift_card and gift_card.is_valid else 0))
            )
            .join(Products, Carts.product_id == Products.id)
            .filter(Carts.user_id == self.user_id)
            .scalar()
        )
        total_price = max(total_price_query or -float("inf"), 1)
        smt = (
            insert(Orders)
            .from_select(
                [
                    Orders.user_id,
                    Orders.product_id,
                    Orders.quantity,
                    Orders.total_price,
                    Orders.status,
                ],
                select(
                    Carts.user_id,
                    Carts.product_id,
                    Carts.quantity,
                    total_price,
                    literal(status.upper()),
                ).where(Carts.user_id == self.user_id),
            )
            .returning(literal_column("*"))
        )
        self.__db.session.execute(smt).mappings().fetchone()
        if gift_card:
            gift_card.use()

        self.__db.session.query(Carts).filter(Carts.user_id == self.user_id).delete()
        self.__db.session.commit()

    def clear(self, *, product: Product | None = None) -> None:
        from src.server.models import Cart as Carts

        query = self.__db.session.query(Carts).filter(Carts.user_id == self.user_id)
        if product:
            query = query.filter(Carts.product_id == product.id)

        query.delete(synchronize_session=False)
        self.__db.session.commit()

    def products(self) -> list[Product]:
        from src.server.models import Cart as Carts

        query = self.__db.session.query(Carts.product_id, Carts.quantity).filter(Carts.user_id == self.user_id)

        products = []

        for product_id, quantity in query.all():
            product = Product.from_id(self.__db, product_id)
            product.stock = quantity
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
        **_,
    ):
        self.__db = db
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

        return User.from_id(self.__db, self.user_id)

    @staticmethod
    def admin_create(db: SQLAlchemy, *, user: User, amount: int) -> GiftCard:
        from src.server.models import GiftCard as GiftCards

        assert user.is_admin, "Only admins can create gift cards."

        smt = insert(GiftCards).values(user_id=user.id, price=amount, CODE=generate_gift_card_code()).returning(literal_column("*"))
        giftcard = db.session.execute(smt).mappings().fetchone()

        if giftcard is None:
            error = "Gift card not found."
            raise ValueError(error) from None

        db.session.commit()

        return GiftCard(db, **{k.lower(): v for k, v in giftcard.__dict__.items()})

    @classmethod
    def create(cls, db: SQLAlchemy, *, user: User, amount: int) -> GiftCard:
        from src.server.models import GiftCard as GiftCards

        smt = insert(GiftCards).values(user_id=user.id, price=amount, CODE=generate_gift_card_code()).returning(literal_column("*"))
        giftcard = db.session.execute(smt).mappings().fetchone()
        db.session.commit()
        if giftcard is None:
            error = "Gift card not found."
            raise ValueError(error) from None

        return cls(db, **{k.lower(): v for k, v in giftcard.__dict__.items()})

    def use(self) -> None:
        from src.server.models import GiftCard as GiftCards

        if not self.is_valid:
            error = "Gift card is already used."
            raise ValueError(error)

        giftcard = GiftCards.query.get(self.id)
        if giftcard:
            giftcard.USED = 1
            giftcard.USED_AT = arrow.now().format("YYYY-MM-DD HH:mm:ss")

            self.__db.session.commit()

    @property
    def is_valid(self) -> bool:
        return not self.used

    @classmethod
    def exists(cls, db: SQLAlchemy, *, code: str) -> GiftCard:
        from src.server.models import GiftCard as GiftCards

        giftcard = GiftCards.query.filter_by(CODE=code).first()

        if giftcard:
            return cls(db, **{k.lower(): v for k, v in giftcard.__dict__.items()})

        error = "Gift card not found."
        raise ValueError(error) from None

    @classmethod
    def from_code(cls, db: SQLAlchemy, code: str) -> GiftCard | None:
        try:
            return cls.exists(db, code=code)
        except ValueError:
            return None

    @classmethod
    def all(cls, db: SQLAlchemy) -> list[GiftCard]:
        from src.server.models import GiftCard as GiftCards

        giftcards = GiftCards.query.all()

        return [cls(db, **{k.lower(): v for k, v in giftcard.__dict__.items()}) for giftcard in giftcards]
