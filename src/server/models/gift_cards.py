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

    ID = Column(Integer, primary_key=True)
    PRICE = Column(Integer, nullable=False)
    USER_ID = Column(Integer, ForeignKey("USERS.ID", ondelete="CASCADE"), nullable=False)
    CODE = Column(TEXT, nullable=False)
    USED = Column(Boolean, default=False)
    CREATED_AT = Column(TIMESTAMP, default=datetime.now)
    USED_AT = Column(TIMESTAMP, default=None)

    __table_args__ = (UniqueConstraint("CODE", name="UNIQUE_CODES"),)
