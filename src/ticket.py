from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import arrow
from flask_sqlalchemy import SQLAlchemy

if TYPE_CHECKING:
    from .user import Admin, User

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
        user: User | Admin,
        replied_to: int | None,
        subject: str,
        message: str,
    ) -> Ticket:
        from .server.models import Tickets

        ticket = Tickets(
            REPLIED_TO=replied_to, USER_ID=user.id, SUBJECT=subject, MESSAGE=message
        )
        db.session.add(ticket)
        db.session.commit()

        return cls(
            db,
            id=ticket.ID,
            replied_to=ticket.REPLIED_TO,
            user_id=ticket.USER_ID,
            subject=ticket.SUBJECT,
            message=ticket.MESSAGE,
            status=ticket.STATUS,
            created_at=ticket.CREATED_AT,
        )

    @classmethod
    def from_id(cls, db: SQLAlchemy, id: int) -> Ticket:
        from .server.models import Tickets

        ticket = Tickets.query.get(id)
        if ticket is None:
            raise ValueError(f"Ticket with id {id} does not exist.")

        return cls(
            db,
            id=ticket.ID,
            replied_to=ticket.REPLIED_TO,
            user_id=ticket.USER_ID,
            subject=ticket.SUBJECT,
            message=ticket.MESSAGE,
            status=ticket.STATUS,
            created_at=ticket.CREATED_AT,
        )

    def update_status(self, status: VALID_STATUS) -> None:
        from .server.models import Tickets

        self.db.session.query(Tickets).filter(Tickets.ID == self.id).update(
            {"STATUS": status}
        )
        self.db.session.commit()

    def reply(self, user: User | Admin, message: str) -> Ticket:
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
        from .server.models import Tickets

        all_tickets = Tickets.query.all()
        return [
            cls(
                db,
                id=ticket.ID,
                replied_to=ticket.REPLIED_TO,
                user_id=ticket.USER_ID,
                subject=ticket.SUBJECT,
                message=ticket.MESSAGE,
                status=ticket.STATUS,
                created_at=ticket.CREATED_AT,
            )
            for ticket in all_tickets
        ]

    @classmethod
    def get_by_status(cls, db: SQLAlchemy, *, status: VALID_STATUS) -> list[Ticket]:
        from .server.models import Tickets

        tickets = Tickets.query.filter_by(STATUS=status).all()
        return [
            cls(
                db,
                id=ticket.ID,
                replied_to=ticket.REPLIED_TO,
                user_id=ticket.USER_ID,
                subject=ticket.SUBJECT,
                message=ticket.MESSAGE,
                status=ticket.STATUS,
                created_at=ticket.CREATED_AT,
            )
            for ticket in tickets
        ]

    @classmethod
    def user_tickets(cls, db: SQLAlchemy, user: User) -> list[Ticket]:
        from .server.models import Tickets

        tickets = Tickets.query.filter_by(USER_ID=user.id).all()
        return [
            cls(
                db,
                id=ticket.ID,
                replied_to=ticket.REPLIED_TO,
                user_id=ticket.USER_ID,
                subject=ticket.SUBJECT,
                message=ticket.MESSAGE,
                status=ticket.STATUS,
                created_at=ticket.CREATED_AT,
            )
            for ticket in tickets
        ]
