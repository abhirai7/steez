from datetime import datetime

from sqlalchemy import DECIMAL, TEXT, TIMESTAMP, VARCHAR, Column, ForeignKey, Integer

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

    ID = Column(Integer, primary_key=True)
    UNIQUE_ID = Column(VARCHAR(16), nullable=False)
    NAME = Column(VARCHAR(255), nullable=False)
    PRICE = Column(DECIMAL(10, 2), nullable=False)
    DISPLAY_PRICE = Column(DECIMAL(10, 2))
    DESCRIPTION = Column(TEXT, nullable=False)
    STOCK = Column(Integer, default=-1)
    SIZE = Column(TEXT, default=None)
    CATEGORY = Column(Integer, ForeignKey("CATEGORIES.ID", ondelete="CASCADE"), nullable=False)
    KEYWORDS = Column(TEXT, default="")
    CREATED_AT = Column(TIMESTAMP, default=datetime.now)
