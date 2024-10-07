from __future__ import annotations

from sqlalchemy import TEXT, Column, Integer

from src.server import db

from typing import cast

class Categories(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `CATEGORIES` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `NAME`      TEXT            UNIQUE          NOT NULL,
        `DESCRIPTION` TEXT          NOT NULL
    );
    """

    __tablename__ = "CATEGORIES"

    ID: int = cast(int, Column(Integer, primary_key=True, autoincrement=True))
    NAME: str = cast(str, Column(TEXT, nullable=False, unique=True))
    DESCRIPTION: str = cast(str, Column(TEXT, nullable=False))

    def __repr__(self) -> str:
        return f"<Category {self.NAME}>"