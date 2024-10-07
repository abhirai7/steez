from datetime import datetime

from sqlalchemy import CHAR, TIMESTAMP, VARCHAR, Column, Integer, String

from src.server import db


class Users(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `USERS` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `EMAIL`     VARCHAR(255)    UNIQUE          NOT NULL,
        `PASSWORD`  CHAR(64)        NOT NULL,
        `NAME`      VARCHAR(255)    NOT NULL,
        `ROLE`      CHAR(5)         DEFAULT        'USER',
        `ADDRESS`   TEXT            NOT NULL,
        `PHONE`     CHAR(10)        NOT NULL,

        `CREATED_AT` TIMESTAMP      DEFAULT         CURRENT_TIMESTAMP
    );
    """

    __tablename__ = "USERS"

    ID = Column(Integer, primary_key=True)
    EMAIL = Column(VARCHAR(255), unique=True, nullable=False)
    PASSWORD = Column(VARCHAR(64), nullable=False)
    NAME = Column(VARCHAR(255), nullable=False)
    ROLE = Column(CHAR(5), default="USER")
    ADDRESS = Column(String(), nullable=False)
    PHONE = Column(CHAR(10), nullable=False)
    CREATED_AT = Column(TIMESTAMP, default=datetime.now)
