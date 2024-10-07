from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint

from src.server import db

from typing import cast

class Carts(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `CARTS` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `USER_ID`   INTEGER         NOT NULL,
        `PRODUCT_ID` INTEGER        NOT NULL,
        `QUANTITY`  INTEGER         NOT NULL,

        FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,
        FOREIGN KEY (`PRODUCT_ID`)  REFERENCES `PRODUCTS`(`ID`) ON DELETE CASCADE,

        CONSTRAINT `UNIQUE_CART`    UNIQUE (`USER_ID`, `PRODUCT_ID`)
    );
    """

    __tablename__ = "CARTS"

    ID: int = cast(int, Column(Integer, primary_key=True))
    USER_ID: int = cast(int, Column(Integer, ForeignKey("USERS.ID", ondelete="CASCADE"), nullable=False))
    PRODUCT_ID: int = cast(int, Column(Integer, ForeignKey("PRODUCTS.ID", ondelete="CASCADE"), nullable=False))
    QUANTITY: int = cast(int, Column(Integer, nullable=False))

    __table_args__ = (UniqueConstraint("USER_ID", "PRODUCT_ID", name="UNIQUE_CART"),)

    def __repr__(self) -> str:
        return f"<Cart {self.ID}>"
