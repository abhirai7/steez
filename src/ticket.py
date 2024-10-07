from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

import arrow

if TYPE_CHECKING:
    from .user import Admin, User


class Ticket:
    def __init__(
        self,
        conn: sqlite3.Connection,
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
        self.conn = conn
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

            self._user = User.from_id(self.conn, self.user_id)
        return self._user

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        *,
        user: User | Admin,
        replied_to: int | None,
        subject: str,
        message: str,
    ) -> Ticket:
        query = r"""
            INSERT INTO TICKETS (REPLIED_TO, USER_ID, SUBJECT, MESSAGE) VALUES (?, ?, ?, ?) RETURNING *
        """

        cursor = conn.cursor()
        cursor.execute(query, (replied_to, user.id, subject, message))
        data = cursor.fetchone()
        conn.commit()

        return cls(conn, **data)

    @classmethod
    def from_id(cls, conn: sqlite3.Connection, id: int) -> Ticket:
        query = r"""
            SELECT * FROM TICKETS WHERE ID = ?
        """

        cursor = conn.cursor()
        cursor.execute(query, (id,))
        data = cursor.fetchone()

        return cls(conn, **data)

    def update_status(self, status: str) -> None:
        valid_status = ["OPEN", "PROC", "CLOS"]
        query = r"""
            UPDATE TICKETS SET STATUS = ? WHERE ID = ?
        """
        if status not in valid_status:
            raise ValueError("Invalid status")

        cursor = self.conn.cursor()
        cursor.execute(query, (status, self.id))
        self.conn.commit()

    def reply(self, user: User | Admin, message: str) -> Ticket:
        return Ticket.create(
            self.conn,
            user=user,
            replied_to=self.id,
            subject=self.subject,
            message=message,
        )

    @property
    def reference(self) -> Ticket | None:
        if not self._replied_to:
            return None
        return Ticket.from_id(self.conn, self._replied_to)

    def chain(self) -> list[Ticket]:
        chain: list[Ticket] = [self]
        current = self
        while current.reference:
            current = current.reference
            chain.append(current)
        return chain

    @classmethod
    def all(cls, conn: sqlite3.Connection) -> list[Ticket]:
        query = r"""
            SELECT * FROM TICKETS
        """

        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

        return [cls(conn, **row) for row in data]

    @classmethod
    def open(cls, conn: sqlite3.Connection) -> list[Ticket]:
        query = r"""
            SELECT * FROM TICKETS WHERE STATUS = 'OPEN'
        """

        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

        return [cls(conn, **row) for row in data]

    @classmethod
    def closed(cls, conn: sqlite3.Connection) -> list[Ticket]:
        query = r"""
            SELECT * FROM TICKETS WHERE STATUS = 'CLOS'
        """

        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

        return [cls(conn, **row) for row in data]

    @classmethod
    def processing(cls, conn: sqlite3.Connection) -> list[Ticket]:
        query = r"""
            SELECT * FROM TICKETS WHERE STATUS = 'PROC'
        """

        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

        return [cls(conn, **row) for row in data]

    @classmethod
    def user_tickets(cls, conn: sqlite3.Connection, user: User) -> list[Ticket]:
        query = r"""
            SELECT * FROM TICKETS WHERE USER_ID = ?
        """

        cursor = conn.cursor()
        cursor.execute(query, (user.id,))
        data = cursor.fetchall()

        return [cls(conn, **row) for row in data]
