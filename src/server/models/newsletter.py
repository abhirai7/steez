from sqlalchemy import TEXT, Column, Integer

from src.server import db


class Newsletter(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(TEXT, unique=True)
