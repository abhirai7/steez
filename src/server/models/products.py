from __future__ import annotations

from datetime import datetime

from sqlalchemy import DECIMAL, TEXT, TIMESTAMP, VARCHAR, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.server import db


class Products(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `PRODUCTS` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `UNIQUE_ID` VARCHAR(16)     NOT NULL,
        `NAME`      VARCHAR(255)    NOT NULL,
        `PRICE`     DECIMAL(10, 2)  NOT NULL,
        `DISPLAY_PRICE` DECIMAL(10, 2),
        `DESCRIPTION` TEXT          NOT NULL,
        `STOCK`     INTEGER         DEFAULT         -1,
        `SIZE`      TEXT            DEFAULT         NULL,
        `CATEGORY`  INTEGER         NOT NULL,
        `KEYWORDS`  TEXT            DEFAULT         "",

        `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,

        FOREIGN KEY (`CATEGORY`)    REFERENCES `CATEGORIES`(`ID`) ON DELETE CASCADE
    );
    """

    __tablename__ = "PRODUCTS"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    UNIQUE_ID: Mapped[str] = mapped_column(VARCHAR(16), nullable=False)
    NAME: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    PRICE: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    DISPLAY_PRICE: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    DESCRIPTION: Mapped[str] = mapped_column(TEXT, nullable=False)
    STOCK: Mapped[int] = mapped_column(Integer, default=-1)
    SIZE: Mapped[str] = mapped_column(TEXT, default=None)
    CATEGORY: Mapped[int] = mapped_column(Integer, ForeignKey("CATEGORIES.ID", ondelete="CASCADE"), nullable=False)
    KEYWORDS: Mapped[str] = mapped_column(TEXT, default="")
    CREATED_AT: Mapped[int] = mapped_column(TIMESTAMP, default=datetime.now)
