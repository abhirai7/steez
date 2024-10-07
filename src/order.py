from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import arrow

if TYPE_CHECKING:
    from .product import Product
    from .user import User

from flask_sqlalchemy import SQLAlchemy

VALID_STATUS = Literal["PEND", "CONF", "PAID", "COD"]
# PEND - Pending
# CONF - Confirmed
# PAID - Paid
# COD - Cash on Delivery


class Order:
    def __init__(
        self,
        db: SQLAlchemy,
        *,
        id: int,
        user_id: int,
        product_id: int,
        quantity: int,
        total_price: float,
        created_at: str,
        status: str = "PEND",
        razorpay_order_id: str | None = None,
    ) -> None:
        self.__db = db
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
        self.total_price = total_price
        self.created_at = arrow.get(created_at)
        self.status = status
        self.razorpay_order_id = razorpay_order_id

    def is_recent(self, days: int = 7) -> bool:
        return self.created_at > arrow.utcnow().shift(days=-days)

    @classmethod
    def create(
        cls,
        db: SQLAlchemy,
        user_id: int,
        product_id: int,
        quantity: int,
        total_price: float,
    ) -> Order:
        from src.server.models import Orders

        order = Orders(USER_ID=user_id, PRODUCT_ID=product_id, QUANTITY=quantity, TOTAL_PRICE=total_price)
        db.session.add(order)
        db.session.commit()

        return cls(
            db,
            id=order.ID,
            user_id=order.USER_ID,
            product_id=order.PRODUCT_ID,
            quantity=order.QUANTITY,
            total_price=order.TOTAL_PRICE,
            created_at=order.CREATED_AT,
            status=order.STATUS,
            razorpay_order_id=order.RAZORPAY_ORDER_ID,
        )

    @classmethod
    def from_id(cls, db: SQLAlchemy, order_id: int) -> Order:
        from src.server.models import Orders

        order = Orders.query.filter_by(ID=order_id).first()
        if order is None:
            error = "Order not found."
            raise ValueError(error) from None

        return cls(
            db,
            id=order.ID,
            user_id=order.USER_ID,
            product_id=order.PRODUCT_ID,
            quantity=order.QUANTITY,
            total_price=order.TOTAL_PRICE,
            created_at=order.CREATED_AT,
            status=order.STATUS,
            razorpay_order_id=order.RAZORPAY_ORDER_ID,
        )

    @classmethod
    def from_razorpay_order_id(cls, db: SQLAlchemy, razorpay_order_id: str) -> Order:
        from src.server.models import Orders

        order = Orders.query.filter_by(RAZORPAY_ORDER_ID=razorpay_order_id).first()
        if order is None:
            error = "Order not found."
            raise ValueError(error) from None

        return cls(
            db,
            id=order.ID,
            user_id=order.USER_ID,
            product_id=order.PRODUCT_ID,
            quantity=order.QUANTITY,
            total_price=order.TOTAL_PRICE,
            created_at=order.CREATED_AT,
            status=order.STATUS,
            razorpay_order_id=order.RAZORPAY_ORDER_ID,
        )

    @property
    def user(self) -> User:
        from .user import User

        return User.from_id(self.__db, self.user_id)

    @property
    def product(self) -> Product:
        from .product import Product

        return Product.from_id(self.__db, self.product_id)

    @classmethod
    def all(
        cls,
        db: SQLAlchemy,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Order]:
        from src.server.models import Orders

        orders = Orders.query.limit(limit).offset(offset).all()
        ls = []

        for order in orders:
            ls.append(
                cls(
                    db,
                    id=order.ID,
                    user_id=order.USER_ID,
                    product_id=order.PRODUCT_ID,
                    quantity=order.QUANTITY,
                    total_price=order.TOTAL_PRICE,
                    created_at=order.CREATED_AT,
                    status=order.STATUS,
                    razorpay_order_id=order.RAZORPAY_ORDER_ID,
                )
            )

        return ls

    @classmethod
    def total_count(cls, db: SQLAlchemy) -> int:
        from src.server.models import Orders

        return Orders.query.count()

    def update_order_status(self, *, status: VALID_STATUS, razorpay_order_id: str) -> None:
        from src.server.models import Orders

        assert razorpay_order_id == self.razorpay_order_id

        order_query = Orders.query.filter_by(ID=self.id, STATUS="CONF", USER_ID=self.user_id)
        orders = order_query.all()

        if not orders:
            error = "Order not found."
            raise ValueError(error) from None

        for order in orders:
            order.STATUS = status
            order.RAZORPAY_ORDER_ID = razorpay_order_id

            self.__db.session.commit()

        self.status = status
        self.razorpay_order_id = razorpay_order_id

    @classmethod
    def delete(cls, db: SQLAlchemy, *, order_id: int, user_id: int) -> None:
        from src.server.models import Orders

        db.session.delete(Orders.query.filter_by(ID=order_id, USER_ID=user_id).first())
        db.session.commit()
