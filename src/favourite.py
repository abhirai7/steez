from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product
    from .user import User

from flask_sqlalchemy import SQLAlchemy


class Favourite:
    def __init__(self, db: SQLAlchemy, *, id: int, user_id: int, product_unique_id: str) -> None:
        self.__db = db
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
        from src.server.models import Favourites

        self.__db.session.delete(Favourites.query.get(self.id))

    @classmethod
    def from_id(cls, db: SQLAlchemy, id: int) -> Favourite:
        from src.server.models import Favourites

        favourite = Favourites.query.get(id)
        return cls(db, id=favourite.ID, user_id=favourite.USER_ID, product_unique_id=favourite.PRODUCT_UNIQUE_ID)

    @classmethod
    def add(cls, db: SQLAlchemy, *, user: User, product: Product) -> Favourite:
        from src.server.models import Favourites

        favourite = Favourites(USER_ID=user.id, PRODUCT_UNIQUE_ID=product.unique_id)
        db.session.add(favourite)
        db.session.commit()

        return cls(db, id=favourite.ID, user_id=favourite.USER_ID, product_unique_id=favourite.PRODUCT_UNIQUE_ID)

    @classmethod
    def all(cls, db: SQLAlchemy) -> list[Favourite]:
        from src.server.models import Favourites

        all_favourites = Favourites.query.all()
        return [cls(db, id=fav.ID, user_id=fav.USER_ID, product_unique_id=fav.PRODUCT_UNIQUE_ID) for fav in all_favourites]

    @classmethod
    def from_user(cls, db: SQLAlchemy, *, user: User, product: Product) -> list[Favourite]:
        from src.server.models import Favourites

        return [
            cls(db, id=fav.ID, user_id=fav.USER_ID, product_unique_id=fav.PRODUCT_UNIQUE_ID)
            for fav in Favourites.query.filter_by(USER_ID=user.id, PRODUCT_UNIQUE_ID=product.unique_id)
        ]

    @classmethod
    def exists(cls, db: SQLAlchemy, *, user: User, product: Product) -> bool:
        from src.server.models import Favourites

        return Favourites.query.filter_by(USER_ID=user.id, PRODUCT_UNIQUE_ID=product.unique_id).first() is not None
