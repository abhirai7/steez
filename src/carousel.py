from __future__ import annotations

from typing import TYPE_CHECKING

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
        from src.server.models import Carousels

        caros = db.session.query(Carousels).all()
        return [
            cls(
                db,
                id=caro.ID,
                image=caro.IMAGE,
                heading=caro.HEADING,
                description=caro.DESCRIPTION,
            )
            for caro in caros
        ]

    @classmethod
    def get(cls, db: SQLAlchemy, id: int) -> Carousel:
        from src.server.models import Carousels

        caro = db.session.query(Carousels).filter_by(ID=id).first()
        if not caro:
            raise ValueError("Carousel not found")

        return cls(
            db,
            id=caro.ID,
            image=caro.IMAGE,
            heading=caro.HEADING,
            description=caro.DESCRIPTION,
        )

    @classmethod
    def create(
        cls,
        db: SQLAlchemy,
        *,
        image: str,
        heading: str,
        description: str,
    ) -> Carousel:
        from src.server.models import Carousels

        carousel = Carousels()
        carousel.IMAGE = image
        carousel.HEADING = heading
        carousel.DESCRIPTION = description
        db.session.add(carousel)
        db.session.commit()

        return cls(
            db,
            id=carousel.ID,
            image=carousel.IMAGE,
            heading=carousel.HEADING,
            description=carousel.DESCRIPTION,
        )

    def delete(self):
        from src.server.models import Carousels

        Carousels.query.filter_by(ID=self.id).delete()
