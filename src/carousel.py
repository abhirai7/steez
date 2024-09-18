from __future__ import annotations

import sqlite3

from .utils import get_product_pictures


class Carousel:
    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        id: int,
        image: str,
        heading: str,
        description: str,
    ):
        self.conn = connection
        self.id = id
        self.image = get_product_pictures(image)[0]
        self.heading = heading
        self.description = description

    @classmethod
    def all(cls, connection: sqlite3.Connection) -> list[Carousel]:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM carousel")
        return [cls(connection, **carousel) for carousel in cursor.fetchall()]

    @classmethod
    def get(cls, connection: sqlite3.Connection, id: int) -> Carousel:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM carousel WHERE id = ?", (id,))
        return cls(connection, **cursor.fetchone())

    @classmethod
    def create(
        cls,
        connection: sqlite3.Connection,
        *,
        image: str,
        heading: str,
        description: str,
    ) -> Carousel:
        cursor = connection.cursor()
        query = r"INSERT INTO CAROUSEL (IMAGE, HEADING, DESCRIPTION) VALUES (?, ?, ?) RETURNING *"
        row = cursor.execute(query, (image, heading, description))
        data = row.fetchone()
        connection.commit()
        return cls(connection, **data)

    def delete(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM CAROUSEL WHERE ID = ?", (self.id,))
        self.conn.commit()
