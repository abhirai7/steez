from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    TEXT,
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.server import db


class GiftCards(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `GIFT_CARDS` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `PRICE`     INTEGER         NOT NULL,
        `USER_ID`   INTEGER         NOT NULL,
        `CODE`      TEXT            NOT NULL,
        `USED`      BOOLEAN         DEFAULT         0,
        `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,
        `USED_AT`   TIMESTAMP       DEFAULT         NULL,

        FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,

        CONSTRAINT `UNIQUE_CODES`   UNIQUE (`CODE`)
    );
    """

    __tablename__ = "GIFT_CARDS"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True)
    PRICE: Mapped[int] = mapped_column(Integer, nullable=False)
    USER_ID: Mapped[int] = mapped_column(Integer, ForeignKey("USERS.ID", ondelete="CASCADE"), nullable=False)
    CODE: Mapped[str] = mapped_column(TEXT, nullable=False)
    USED: Mapped[bool] = mapped_column(Boolean, default=False)
    CREATED_AT: Mapped[int] = mapped_column(TIMESTAMP, default=datetime.now)
    USED_AT: Mapped[int] = mapped_column(TIMESTAMP, default=None)

    __table_args__ = (UniqueConstraint("CODE", name="UNIQUE_CODES"),)
