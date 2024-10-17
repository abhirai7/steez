from __future__ import annotations

from typing import TYPE_CHECKING

import arrow

if TYPE_CHECKING:
    from .order import Order
    from .user import User

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert, literal_column


class Refund:
    def __init__(
        self,
        db: SQLAlchemy,
        *,
        id: int,
        order_id: int,
        reason: str,
        created_at: str,
        **_,
    ):
        self.db = db
        self.id = id
        self.order_id = order_id
        self.reason = reason
        self.created_at = arrow.get(created_at)

    @classmethod
    def create(cls, db: SQLAlchemy, *, order: Order, reason: str) -> Refund:
        from .server.models import ReturnRequest

        smt = insert(ReturnRequest).values(order_id=order.id, reason=reason).returning(literal_column("*"))
        refund = db.session.execute(smt).mappings().first()
        db.session.commit()

        assert refund is not None

        return cls(db, **{k.lower(): v for k, v in refund.items()})

    @classmethod
    def from_id(cls, db: SQLAlchemy, id: int) -> Refund:
        from .server.models import ReturnRequest

        refund = ReturnRequest.query.get(id)
        if refund is None:
            raise ValueError(f"Refund with id {id} does not exist.")

        return cls(
            db,
            id=refund.id,
            order_id=refund.order_id,
            reason=refund.reason,
            created_at=refund.created_at,
        )

    @classmethod
    def from_order(cls, db: SQLAlchemy, order: Order) -> Refund:
        from .server.models import ReturnRequest

        refund = ReturnRequest.query.filter_by(order_id=order.id).first()
        if refund is None:
            raise ValueError(f"Refund for order with id {order.id} does not exist.")

        return cls(
            db,
            id=refund.id,
            order_id=refund.order_id,
            reason=refund.reason,
            created_at=refund.created_at,
        )

    @classmethod
    def all(cls, db: SQLAlchemy, *, user: User | None = None) -> list[Refund]:
        from .server.models import Order as Orders
        from .server.models import ReturnRequest

        query = ReturnRequest.query
        if user:
            query = query.join(Orders).filter(Orders.user_id == user.id)

        refunds = query.all()
        return [
            cls(
                db,
                id=refund.id,
                order_id=refund.order_id,
                reason=refund.reason,
                created_at=refund.created_at,
            )
            for refund in refunds
        ]
