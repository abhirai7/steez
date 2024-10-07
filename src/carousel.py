from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import text

from .utils import get_product_pictures

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy
    from typing_extensions import Self


class Carousel:
    def __init__(
        self,
        db: SQLAlchemy,
        *,
        id: int,
        image: str,
        heading: str,
        description: str,
    ):
        self.db = db
        self.id = id
        self.image = get_product_pictures(image)[0]
        self.heading = heading
        self.description = description

    @classmethod
    def all(cls, db: SQLAlchemy) -> list[Self]:
        with db.session() as conn:
            result = conn.execute(text("SELECT * FROM CAROUSELS"))
            return [cls(db, **carousel) for carousel in result.mappings()]

    @classmethod
    def get(cls, db: SQLAlchemy, id: int) -> Carousel:
        with db.session() as conn:
            result = conn.execute(
                text("SELECT * FROM CAROUSELS WHERE ID = :id"), {"id": id}
            )
            for carousel in result.mappings():
                return cls(db, **carousel)

        raise ValueError(f"Carousel with ID {id} not found")

    @classmethod
    def create(
        cls,
        db: SQLAlchemy,
        *,
        image: str,
        heading: str,
        description: str,
    ) -> Carousel:
        with db.session() as conn:
            result = conn.execute(
                text(
                    "INSERT INTO CAROUSELS (IMAGE, HEADING, DESCRIPTION) VALUES (:image, :heading, :description) RETURNING *"
                ),
                {"image": image, "heading": heading, "description": description},
            )
            carousel = result.mappings().fetchone()
            if carousel is None:
                raise ValueError("Carousel not created")

            return cls(db, **carousel)

    def delete(self):
        from src.server.models import Carousels

        Carousels.query.filter_by(ID=self.id).delete()
