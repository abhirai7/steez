from __future__ import annotations

from typing import TYPE_CHECKING

import arrow

if TYPE_CHECKING:
    from .favourite import Favourite
    from .order import Order
    from .product import VALID_STARS, Cart, GiftCard, Product
    from .type_hints import Client as RazorpayClient
    from .type_hints import RazorPayOrderDict

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert, literal_column


class User:
    def __init__(
        self,
        db: SQLAlchemy,
        *,
        id: int,
        email: str,
        name: str,
        password: str,
        created_at: str | None = None,
        role: str = "USER",
        address: str,
        phone: str,
        **_,
    ):
        self.__db = db
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        self.created_at = arrow.get(created_at) if created_at else arrow.now()
        self.address = address
        self.phone = phone

        self.is_active = True
        self.is_anonymous = False
        self.is_authenticated = True
        self.__role = role

    def get_id(self):
        return str(self.id)

    @property
    def orders(self) -> list[Order]:
        from .order import Order
        from .server.models import Orders

        orders = Orders.query.filter_by(user_id=self.id).order_by(Orders.CREATED_AT.desc()).all()

        return [Order(self.__db, **{k.lower(): v for k, v in row.__dict__.items()}) for row in orders]

    @property
    def is_admin(self):
        return self.role == "ADMIN"

    @property
    def role(self):
        return self.__role

    @property
    def cart(self) -> Cart:
        from .product import Cart

        return Cart(self.__db, user_id=self.id)

    def __str__(self) -> str:
        return f"User(id={self.id!r} email={self.email!r} created_at={self.created_at!r})"

    @classmethod
    def from_email(cls, db: SQLAlchemy, *, email: str, password: str) -> User:
        from .server import bcrypt
        from .server.models import Users

        user = Users.query.filter_by(EMAIL=email, ROLE="USER").first()

        if user is None or not bcrypt.check_password_hash(user.PASSWORD, password):
            error = "User not found. Either email or password is incorrect."
            raise ValueError(error) from None

        return cls(db, **{k.lower(): v for k, v in user.__dict__.items()})

    @classmethod
    def from_id(cls, db: SQLAlchemy, user_id: int):
        from .server.models import Users

        user = Users.query.get(user_id)
        if user is None:
            error = "User not found."
            raise ValueError(error) from None

        return cls(db, **{k.lower(): v for k, v in user.__dict__.items()})

    @classmethod
    def create(
        cls,
        db: SQLAlchemy,
        *,
        email: str,
        name: str,
        password_hash: str,
        address: str,
        phone: str,
        role: str = "USER",
    ) -> User:
        from .server.models import Users

        smt = (
            insert(Users)
            .values(
                EMAIL=email,
                NAME=name,
                PASSWORD=password_hash,
                ADDRESS=address,
                PHONE=phone,
                ROLE=role,
            )
            .returning(literal_column("*"))
        )
        user = db.session.execute(smt).mappings().first()
        assert user is not None
        db.session.commit()

        return cls(db, **{k.lower(): v for k, v in user.items()})

    def add_review(self, *, product: Product, stars: VALID_STARS, review: str):
        product.add_review(user_id=self.id, stars=stars, review=review)

    def del_review(self, *, product: Product) -> None:
        product.delete_review(user_id=self.id)

    def add_to_cart(self, *, product: Product, quantity: int | None = 1) -> None:
        self.cart.add_product(product=product, quantity=quantity)

    def remove_from_cart(self, *, product: Product, _: int = 1) -> None:
        self.cart.remove_product(product=product)

    def clear_cart(self, *, product: Product | None = None) -> None:
        self.cart.clear(product=product)

    def add_to_fav(self, *, product: Product) -> Favourite:
        from .favourite import Favourite

        return Favourite.add(self.__db, user=self, product=product)

    def remove_from_fav(self, *, product: Product) -> None:
        from .favourite import Favourite

        if fav := Favourite.from_user(self.__db, user=self, product=product):
            fav[0].delete()

    def is_fav(self, *, product: Product) -> bool:
        return Favourite.exists(self.__db, user=self, product=product)

    def partial_checkout(self, *, gift_code: str = "", status: str | None = None) -> list[Order]:
        from .product import GiftCard

        gift_card = GiftCard.from_code(self.__db, code=gift_code)
        self.cart.update_to_database(gift_card=gift_card, status=status or "PEND")
        self.clear_cart()

        return self.__fetch_orders("PEND")

    def __fetch_orders(self, status: str | None = None) -> list[Order]:
        from .order import Order
        from .server.models import Orders

        orders = (
            self.__db.session.query(Orders)
            .filter_by(user_id=self.id, status=status or "PEND")
            .order_by(Orders.CREATED_AT.desc())
            .all()
        )

        return [Order(self.__db, **{k.lower(): v for k, v in order.__dict__.items()}) for order in orders]

    def full_checkout(self, razorpay_client: RazorpayClient, *, gift_code: str = "") -> RazorPayOrderDict:
        from .server.models import Orders

        orders: list[Order] = self.partial_checkout(gift_code=gift_code)

        if not orders:
            error = "No orders found to checkout."
            order_id = (
                self.__db.session.query(Orders.RAZORPAY_ORDER_ID)
                .filter(
                    Orders.USER_ID == self.id,
                    Orders.STATUS != "PAID",
                    Orders.RAZORPAY_ORDER_ID.isnot(None),
                )
                .scalar()
            )
            if order_id:
                return razorpay_client.order.fetch(order_id)

            raise ValueError(error)

        total_price = sum(order.total_price for order in orders)

        final_payload = {
            "amount": int(total_price * 100),
            "currency": "INR",
            "notes": {
                "products": [
                    {
                        "name": order.product.name,
                        "quantity": order.quantity,
                        "price": order.product.price,
                    }
                    for order in orders
                ],
                "user": {
                    "name": self.name,
                    "email": self.email,
                    "phone": self.phone,
                    "id": self.id,
                },
                "gift_card": False,
            },
        }

        api_response: RazorPayOrderDict = razorpay_client.order.create(final_payload)
        order_id = api_response["id"]

        update = (
            self.__db.session.query(Orders)
            .filter(
                Orders.USER_ID == self.id,
                Orders.STATUS == "PEND",
                Orders.RAZORPAY_ORDER_ID.is_(None),
            )
            .update({Orders.RAZORPAY_ORDER_ID: order_id, Orders.STATUS: "CONF"})
        )

        if update == 0:
            error = "No orders found to checkout."
            raise ValueError(error)

        self.__db.session.commit()

        assert self.__check_api_response(full_paylaod=final_payload, api_response=api_response)

        return api_response  # type: ignore

    def __check_api_response(self, *, full_paylaod: dict, api_response: RazorPayOrderDict) -> bool:
        amount_correct = full_paylaod["amount"] == api_response["amount"]
        currency_correct = full_paylaod["currency"] == api_response["currency"]
        notes_correct = full_paylaod["notes"] == api_response["notes"]
        status_correct = api_response["status"] == "created"

        return amount_correct and currency_correct and notes_correct and status_correct

    @staticmethod
    def exists(db: SQLAlchemy, email: str) -> bool:
        from .server.models import Users

        return db.session.query(Users).filter_by(EMAIL=email).scalar() is not None

    @classmethod
    def all(
        cls,
        db: SQLAlchemy,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[User]:
        from .server.models import Users

        users = db.session.query(Users).filter_by(ROLE="USER").limit(limit).offset(offset).all()
        return [cls(db, **{k.lower(): v for k, v in user.__dict__.items()}) for user in users]

    @staticmethod
    def total_count(db: SQLAlchemy) -> int:
        from .server.models import Users

        return db.session.query(Users).filter_by(ROLE="USER").count()

    def full_checkout_giftcard(self, razorpay_client: RazorpayClient, amount: int) -> RazorPayOrderDict:
        final_payload = {
            "amount": int(amount * 100),
            "currency": "INR",
            "notes": {
                "user": {
                    "name": self.name,
                    "email": self.email,
                    "phone": self.phone,
                    "id": self.id,
                },
                "gift_card": True,
            },
        }

        api_response: RazorPayOrderDict = razorpay_client.order.create(final_payload)

        assert self.__check_api_response(full_paylaod=final_payload, api_response=api_response)

        return api_response

    def _buy_gift_card(self, amount: int) -> GiftCard:
        from .product import GiftCard

        return GiftCard.create(self.__db, user=self, amount=amount)


class Admin(User):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def from_email(cls, db: SQLAlchemy, *, password: str) -> Admin:
        from .server import bcrypt
        from .server.models import Users

        users = Users.query.filter_by(ROLE="ADMIN").all()

        user = None

        for usr in users:
            if bcrypt.check_password_hash(usr.PASSWORD, password):
                user = usr
                break

        if user is None:
            error = "Admin not found. Either email or password is incorrect."
            raise ValueError(error) from None

        return cls(
            db,
            **{k.lower(): v for k, v in {k.lower(): v for k, v in user.__dict__.items()}.items()},
        )

    @classmethod
    def delete_user(cls, db: SQLAlchemy, user_id: int) -> None:
        from .server.models import Users

        db.session.query(Users).filter_by(ID=user_id, ROLE="USER").delete()
        db.session.commit()

    @classmethod
    def delete_product(cls, db: SQLAlchemy, product_id: int) -> None:
        from .server.models import Products

        db.session.query(Products).filter_by(ID=product_id).delete()
