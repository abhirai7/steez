from datetime import datetime

from sqlalchemy import TIMESTAMP, VARCHAR, Column, ForeignKey, Integer

from src.server import db


class Reviews(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `REVIEWS` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `USER_ID`   INTEGER         NOT NULL,
        `PRODUCT_ID` INTEGER        NOT NULL,
        `STARS`     INTEGER         NOT NULL,
        `REVIEW`    VARCHAR(255)    NOT NULL,
        `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,

        FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,
        FOREIGN KEY (`PRODUCT_ID`)  REFERENCES `PRODUCTS`(`ID`) ON DELETE CASCADE
    );
    """

    __tablename__ = "REVIEWS"

    ID = Column(Integer, primary_key=True)
    USER_ID = Column(Integer, ForeignKey("USERS.ID", ondelete="CASCADE"), nullable=False)
    PRODUCT_ID = Column(Integer, ForeignKey("PRODUCTS.ID", ondelete="CASCADE"), nullable=False)
    STARS = Column(Integer, nullable=False)
    REVIEW = Column(VARCHAR(255), nullable=False)
    CREATED_AT = Column(TIMESTAMP, default=datetime.now)
