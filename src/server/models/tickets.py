from datetime import datetime

from sqlalchemy import CHAR, TEXT, TIMESTAMP, Column, ForeignKey, Integer

from src.server import db


class Tickets(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `TICKETS` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `REPLIED_TO` INTEGER        DEFAULT         NULL,
        `USER_ID`   INTEGER         NOT NULL,
        `SUBJECT`   TEXT            NOT NULL,
        `MESSAGE`   TEXT            NOT NULL,
        -- OPEN, PROC, CLOS
        `STATUS`    CHAR(4)         DEFAULT         'OPEN',
        `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP,

        FOREIGN KEY (`USER_ID`)     REFERENCES `USERS`(`ID`)    ON DELETE CASCADE,
        FOREIGN KEY (`REPLIED_TO`)  REFERENCES `TICKETS`(`ID`)  ON DELETE CASCADE
    );
    """

    __tablename__ = "TICKETS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    REPLIED_TO = Column(Integer, ForeignKey("TICKETS.ID", ondelete="CASCADE"), default=None)
    USER_ID = Column(Integer, ForeignKey("USERS.ID", ondelete="CASCADE"), nullable=False)
    SUBJECT = Column(TEXT, nullable=False)
    MESSAGE = Column(TEXT, nullable=False)
    STATUS = Column(CHAR(4), default="OPEN")
    CREATED_AT = Column(TIMESTAMP, default=datetime.now)
