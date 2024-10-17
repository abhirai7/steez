from __future__ import annotations

from sqlalchemy import TEXT, Column, Integer

from src.server import db


class Carousel(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(TEXT, nullable=False)
    heading = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
