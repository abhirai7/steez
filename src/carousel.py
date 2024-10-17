from __future__ import annotations

from typing import TYPE_CHECKING

from .utils import get_product_pictures

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy
    from typing_extensions import Self

from sqlalchemy import insert, literal_column, select


class Carousel:
    def __init__(
        self,
        db: SQLAlchemy,
        *,
        id: int,
        image: str,
        heading: str,
        description: str,
        **_,
    ):
        self.db = db
        self.id = id
        self.image = get_product_pictures(image)[0]
        self.heading = heading
        self.description = description

    @classmethod
    def all(cls, db: SQLAlchemy) -> list[Self]:
        from src.server.models import Carousel as Carousels

        smt = select(Carousels)
        carousels = db.session.execute(smt).mappings().all()
        return [cls(db, **caro) for caro in carousels]

    @classmethod
    def get(cls, db: SQLAlchemy, id: int) -> Carousel:
        from src.server.models import Carousel as Carousels

        caro = db.session.query(Carousels).get(id)
        if not caro:
            raise ValueError("Carousel not found")

        return cls(
            db,
            id=caro.id,
            image=caro.image,
            heading=caro.heading,
            description=caro.description,
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
        from src.server.models import Carousel as Carousels

        smt = (
            insert(Carousels)
            .values(
                image=image,
                heading=heading,
                description=description,
            )
            .returning(literal_column("*"))
        )

        carousel = db.session.execute(smt).mappings().first()
        db.session.commit()

        assert carousel is not None

        return cls(db, **{k.lower(): v for k, v in carousel.items()})

    def delete(self):
        from src.server.models import Carousel as Carousels

        Carousels.query.filter_by(id=self.id).delete()
