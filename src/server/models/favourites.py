from __future__ import annotations

from sqlalchemy import VARCHAR, Column, ForeignKey, Integer, UniqueConstraint

from src.server import db


class Favourites(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `FAVOURITES` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `USER_ID`   INTEGER         NOT NULL,
        `PRODUCT_UNIQUE_ID` VARCHAR(16)        NOT NULL,

        FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,

        CONSTRAINT `UNIQUE_FAVORITE` UNIQUE (`USER_ID`, `PRODUCT_UNIQUE_ID`) ON CONFLICT REPLACE
    );
    """

    __tablename__ = "FAVOURITES"

    ID = Column(Integer, primary_key=True)
    USER_ID = Column(Integer, ForeignKey("USERS.ID", ondelete="CASCADE"), nullable=False)
    PRODUCT_UNIQUE_ID = Column(VARCHAR(16), nullable=False)

    __table_args__ = (UniqueConstraint("USER_ID", "PRODUCT_UNIQUE_ID", name="UNIQUE_FAVORITE"),)
