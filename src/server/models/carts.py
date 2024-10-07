from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint

from src.server import db


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

    ID = Column(Integer, primary_key=True)
    USER_ID = Column(Integer, ForeignKey("USERS.ID", ondelete="CASCADE"), nullable=False)
    PRODUCT_ID = Column(Integer, ForeignKey("PRODUCTS.ID", ondelete="CASCADE"), nullable=False)
    QUANTITY = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("USER_ID", "PRODUCT_ID", name="UNIQUE_CART"),)
