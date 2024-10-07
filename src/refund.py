from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

import arrow

if TYPE_CHECKING:
    from .order import Order
    from .user import User


class Refund:
    def __init__(
        self,
        conn: sqlite3.Connection,
        *id: int,
        order_id: int,
        reason: str,
        created_at: str,
        **_,
    ):
        self.conn = conn
        self.id = id
        self.order_id = order_id
        self.reason = reason
        self.created_at = arrow.get(created_at)

    @classmethod
    def create(cls, conn: sqlite3.Connection, *, order: Order, reason: str) -> Refund:
        cur = conn.cursor()
        query = r"""
            INSERT INTO RETURN_REQUESTS (ORDER_ID, REASON) 
            VALUES (?, ?) RETURNING *
        """
        cur.execute(query, (order.id, reason))
        row = cur.fetchone()
        conn.commit()

        return cls(conn, **row)

    @classmethod
    def from_id(cls, conn: sqlite3.Connection, id: int) -> Refund:
        cur = conn.cursor()
        query = r"""
            SELECT * FROM RETURN_REQUESTS WHERE ID = ?
        """
        cur.execute(query, (id,))
        row = cur.fetchone()
        return cls(conn, **row)

    @classmethod
    def from_order(cls, conn: sqlite3.Connection, order: Order) -> Refund:
        cur = conn.cursor()
        query = r"""
            SELECT * FROM RETURN_REQUESTS WHERE ORDER_ID = ?
        """
        cur.execute(query, (order.id,))
        row = cur.fetchone()
        return cls(conn, **row)

    @classmethod
    def all(cls, conn: sqlite3.Connection, *, user: User | None = None) -> list[Refund]:
        cur = conn.cursor()
        if user:
            query = r"""
                SELECT * FROM RETURN_REQUESTS
                WHERE ORDER_ID IN (
                    SELECT ID FROM ORDERS WHERE USER_ID = ?
                )
            """
            cur.execute(query, (user.id,))
        else:
            query = r"""
                SELECT * FROM RETURN_REQUESTS
            """
            cur.execute(query)

        rows = cur.fetchall()
        return [cls(conn, **row) for row in rows]
