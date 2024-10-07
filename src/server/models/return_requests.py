from datetime import datetime

from sqlalchemy import TEXT, TIMESTAMP, Column, ForeignKey, Integer

from src.server import db


class ReturnRequests(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `RETURN_REQUESTS` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `ORDER_ID`  INTEGER         NOT NULL,
        `REASON`    TEXT            NOT NULL,
        `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,

        FOREIGN KEY (`ORDER_ID`)    REFERENCES `ORDERS`(`ID`)   ON DELETE CASCADE
    );
    """

    __tablename__ = "RETURN_REQUESTS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ORDER_ID = Column(Integer, ForeignKey("ORDERS.ID", ondelete="CASCADE"), nullable=False)
    REASON = Column(TEXT, nullable=False)
    CREATED_AT = Column(TIMESTAMP, default=datetime.now)
