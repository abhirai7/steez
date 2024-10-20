from __future__ import annotations

from typing import TYPE_CHECKING

from flask_security.core import RoleMixin, UserMixin, WebAuthnMixin

if TYPE_CHECKING:
    from .favourite import Favourite
    from .order import Order
    from .product import VALID_STARS, Cart, GiftCard, Product
    from .type_hints import Client as RazorpayClient
    from .type_hints import RazorPayOrderDict
    from typing_extensions import Self

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


class User(UserMixin):
    db: SQLAlchemy

    if TYPE_CHECKING:  # pragma: no cover
        id: int
        email: str
        username: str | None
        password: str | None
        active: bool
        fs_uniquifier: str
        fs_token_uniquifier: str
        fs_webauthn_user_handle: str
        confirmed_at: datetime | None
        last_login_at: datetime
        current_login_at: datetime
        last_login_ip: str | None
        current_login_ip: str | None
        login_count: int
        tf_primary_method: str | None
        tf_totp_secret: str | None
        tf_phone_number: str | None
        mf_recovery_codes: list[str] | None
        us_phone_number: str | None
        us_totp_secrets: str | bytes | None
        create_datetime: datetime
        update_datetime: datetime
        roles: list[RoleMixin]
        webauthn: list[WebAuthnMixin]

        #
    name: str | None
    phone: str | None

    @property
    def orders(self) -> list[Order]:
        from .order import Order
        from .server.models import Order as Orders

        orders = Orders.query.filter_by(user_id=self.id).order_by(Orders.created_at.desc()).all()

        return [Order(self.db, **{k.lower(): v for k, v in row.__dict__.items()}) for row in orders]

    @property
    def cart(self) -> Cart:
        from .product import Cart

        return Cart(self.db, user_id=self.id)

    @classmethod
    def from_id(cls, db: SQLAlchemy, user_id: int):
        from .server.models import User as Users

        user = Users.query.get(user_id)
        if user is None:
            error = "User not found."
            raise ValueError(error) from None

        return cls(**{k.lower(): v for k, v in user.__dict__.items()})

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

        return Favourite.add(self.db, user=self, product=product)

    def remove_from_fav(self, *, product: Product) -> None:
        from .favourite import Favourite

        if fav := Favourite.from_user(self.db, user=self, product=product):
            fav[0].delete()

    def is_fav(self, *, product: Product) -> bool:
        return Favourite.exists(self.db, user=self, product=product)

    def partial_checkout(self, *, gift_code: str = "", status: str | None = None) -> list[Order]:
        from .product import GiftCard

        gift_card = GiftCard.from_code(self.db, code=gift_code)
        self.cart.update_to_database(gift_card=gift_card, status=status or "PEND")
        self.clear_cart()

        return self.__fetch_orders("PEND")

    def __fetch_orders(self, status: str | None = None) -> list[Order]:
        from .order import Order
        from .server.models import Order as Orders

        orders = (
            self.db.session.query(Orders).filter_by(user_id=self.id, status=status or "PEND").order_by(Orders.created_at.desc()).all()
        )

        return [Order(self.db, **{k.lower(): v for k, v in order.__dict__.items()}) for order in orders]

    def full_checkout(self, razorpay_client: RazorpayClient, *, gift_code: str = "") -> RazorPayOrderDict:
        from .server.models import Order as Orders

        orders: list[Order] = self.partial_checkout(gift_code=gift_code)

        if not orders:
            error = "No orders found to checkout."
            order_id = (
                self.db.session.query(Orders.razorpay_order_id)
                .filter(
                    Orders.user_id == self.id,
                    Orders.status != "PAID",
                    Orders.razorpay_order_id.isnot(None),
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
                        "name": str(order.product.name),
                        "quantity": int(order.quantity),
                        "price": float(order.product.price),
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
            self.db.session.query(Orders)
            .filter(
                Orders.user_id == self.id,
                Orders.status == "PEND",
                Orders.razorpay_order_id.is_(None),
                Orders.seen.is_(False),
            )
            .update(
                {
                    Orders.razorpay_order_id: order_id,
                    Orders.status: "CONF",
                    Orders.seen: True,
                }
            )
        )

        if update == 0:
            error = "No orders found to checkout."
            raise ValueError(error)

        self.db.session.commit()

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
        from .server.models import User as Users

        return db.session.query(Users).filter_by(email=email).scalar() is not None

    @classmethod
    def all(
        cls,
        db: SQLAlchemy,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Self]:
        from .server.models import User as Users

        users = db.session.query(Users).filter_by(ROLE="USER").limit(limit).offset(offset).all()
        return [cls(db=db, **{k.lower(): v for k, v in user.__dict__.items()}) for user in users]

    @staticmethod
    def total_count(db: SQLAlchemy) -> int:
        from .server.models import User as Users

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

        return GiftCard.create(self.db, user=self, amount=amount)

    @classmethod
    def from_usermixin(cls, db: SQLAlchemy, usermixin: UserMixin) -> User:
        return cls(**{k.lower(): v for k, v in usermixin.__dict__.items()}, db=db)
