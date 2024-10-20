from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import arrow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert, literal_column

if TYPE_CHECKING:
    from .user import User

VALID_STATUS = Literal["OPEN", "CLOS", "PROC"]


class Ticket:
    def __init__(
        self,
        db: SQLAlchemy,
        *,
        id: int,
        replied_to: int | None,
        user_id: int,
        subject: str,
        message: str,
        status: str,
        created_at: str,
        **_,
    ):
        self.db = db
        self.id = id
        self._replied_to = replied_to
        self.user_id = user_id
        self.subject = subject
        self.message = message
        self.status = status
        self.created_at = arrow.get(created_at)
        self._user: User | None = None

    @property
    def user(self) -> User:
        if not self._user:
            from .user import User

            self._user = User.from_id(self.db, self.user_id)
        return self._user

    @classmethod
    def create(
        cls,
        db: SQLAlchemy,
        *,
        user: User,
        replied_to: int | None,
        subject: str,
        message: str,
    ) -> Ticket:
        from .server.models import Ticket as Tickets

        smt = (
            insert(Tickets)
            .values(replied_to=replied_to, user_id=user.id, subject=subject, message=message)
            .returning(literal_column("*"))
        )
        ticket = db.session.execute(smt).mappings().first()
        db.session.commit()

        assert ticket is not None

        return cls(db, **{k.lower(): v for k, v in ticket.items()})

    @classmethod
    def from_id(cls, db: SQLAlchemy, id: int) -> Ticket:
        from .server.models import Ticket as Tickets

        ticket = Tickets.query.get(id)
        if ticket is None:
            raise ValueError(f"Ticket with id {id} does not exist.")

        return cls(
            db,
            id=ticket.id,
            replied_to=ticket.replied_to,
            user_id=ticket.user_id,
            subject=ticket.subject,
            message=ticket.message,
            status=ticket.status,
            created_at=ticket.created_at,
        )

    def update_status(self, status: VALID_STATUS) -> None:
        from .server.models import Ticket as Tickets

        self.db.session.query(Tickets).filter(Tickets.id == self.id).update({"status": status})
        self.db.session.commit()

    def reply(self, user: User, message: str) -> Ticket:
        return Ticket.create(
            self.db,
            user=user,
            replied_to=self.id,
            subject=self.subject,
            message=message,
        )

    @property
    def reference(self) -> Ticket | None:
        if not self._replied_to:
            return None
        return Ticket.from_id(self.db, self._replied_to)

    def chain(self) -> list[Ticket]:
        chain: list[Ticket] = [self]
        current = self
        while current.reference:
            current = current.reference
            chain.append(current)
        return chain

    @classmethod
    def all(cls, db: SQLAlchemy) -> list[Ticket]:
        from .server.models import Ticket as Tickets

        all_tickets = Tickets.query.all()
        return [
            cls(
                db,
                id=ticket.id,
                replied_to=ticket.replied_to,
                user_id=ticket.user_id,
                subject=ticket.subject,
                message=ticket.message,
                status=ticket.status,
                created_at=ticket.created_at,
            )
            for ticket in all_tickets
        ]

    @classmethod
    def get_by_status(cls, db: SQLAlchemy, *, status: VALID_STATUS) -> list[Ticket]:
        from .server.models import Ticket as Tickets

        tickets = Tickets.query.filter_by(status=status).all()
        return [
            cls(
                db,
                id=ticket.id,
                replied_to=ticket.replied_to,
                user_id=ticket.user_id,
                subject=ticket.subject,
                message=ticket.message,
                status=ticket.status,
                created_at=ticket.created_at,
            )
            for ticket in tickets
        ]

    @classmethod
    def user_tickets(cls, db: SQLAlchemy, user: User) -> list[Ticket]:
        from .server.models import Ticket as Tickets

        tickets = Tickets.query.filter_by(user_id=user.id).all()
        return [
            cls(
                db,
                id=ticket.id,
                replied_to=ticket.replied_to,
                user_id=ticket.user_id,
                subject=ticket.subject,
                message=ticket.message,
                status=ticket.status,
                created_at=ticket.created_at,
            )
            for ticket in tickets
        ]
