from __future__ import annotations

from sqlalchemy import TEXT, Column, Integer

from src.server import db
from typing import cast

class Carousels(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `CAROUSELS` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `IMAGE`     TEXT            NOT NULL,
        `HEADING`   TEXT            NOT NULL,
        `DESCRIPTION` TEXT          NOT NULL
    );
    """

    __tablename__ = "CAROUSELS"

    ID: int = cast(int, Column(Integer, primary_key=True, autoincrement=True))
    IMAGE: str = cast(str, Column(TEXT, nullable=False))
    HEADING: str = cast(str, Column(TEXT, nullable=False))
    DESCRIPTION: str = cast(str, Column(TEXT, nullable=False))

    def __repr__(self) -> str:
        return f"<Carousel {self.HEADING}>"