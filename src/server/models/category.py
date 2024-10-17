from __future__ import annotations

from sqlalchemy import TEXT, Column, Integer

from src.server import db


class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(TEXT, nullable=False, unique=True)
    description = Column(TEXT, nullable=False)
