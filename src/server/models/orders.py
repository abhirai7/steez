from datetime import datetime

from sqlalchemy import CHAR, DECIMAL, TEXT, TIMESTAMP, Column, ForeignKey, Integer, Boolean

from src.server import db


class Orders(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `ORDERS` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `USER_ID`   INTEGER         NOT NULL,
        `PRODUCT_ID` INTEGER        NOT NULL,
        `QUANTITY`  INTEGER         NOT NULL,
        `TOTAL_PRICE` DECIMAL(10, 2) NOT NULL,
        `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,
        `STATUS`    CHAR(4)         DEFAULT         'PEND',
        `RAZORPAY_ORDER_ID` TEXT    DEFAULT         NULL,
        `SEEN`      BOOLEAN         DEFAULT         FALSE,

        FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,
        FOREIGN KEY (`PRODUCT_ID`)  REFERENCES `PRODUCTS`(`ID`) ON DELETE CASCADE
    );
    """

    __tablename__ = "ORDERS"

    ID = Column(Integer, primary_key=True)
    USER_ID = Column(Integer, ForeignKey("USERS.ID", ondelete="CASCADE"), nullable=False)
    PRODUCT_ID = Column(Integer, ForeignKey("PRODUCTS.ID", ondelete="CASCADE"), nullable=False)
    QUANTITY = Column(Integer, nullable=False)
    TOTAL_PRICE = Column(DECIMAL(10, 2), nullable=False)
    CREATED_AT = Column(TIMESTAMP, default=datetime.now)
    STATUS = Column(CHAR(4), default="PEND")
    RAZORPAY_ORDER_ID = Column(TEXT, default=None)
    SEEN = Column(Boolean, default=False)
