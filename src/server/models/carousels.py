from sqlalchemy import TEXT, Column, Integer

from src.server import db


class Carousels(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `CAROUSELS` (
        `ID`        INTEGER         PRIMARY KEY     AUTOINCREMENT,
        `IMAGE`     TEXT            NOT NULL,
        `HEADING`   TEXT            NOT NULL,
        `DESCRIPTION` TEXT          NOT NULL
    );
    """

    __tablename__ = "CAROUSELS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    IMAGE = Column(TEXT, nullable=False)
    HEADING = Column(TEXT, nullable=False)
    DESCRIPTION = Column(TEXT, nullable=False)
