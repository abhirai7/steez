from sqlalchemy import TEXT, Column, Integer

from src.server import db


class Newsletters(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `NEWSLETTERS` (
        ID          INTEGER         PRIMARY KEY     AUTOINCREMENT,
        EMAIL       TEXT            DEFAULT         "",

        CONSTRAINT `UNIQUE_EMAIL`    UNIQUE (`EMAIL`)
    );
    """

    __tablename__ = "NEWSLETTERS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    EMAIL = Column(TEXT, default="", unique=True)
