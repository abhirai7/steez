from __future__ import annotations

from flask_security.models import fsqla_v3 as fsqla
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.server import db
from src.user import User as _User

__all__ = ["User"]


class User(db.Model, fsqla.FsUserMixin, _User):
    db = db

    address = Column(String(255))
    city = Column(String(255))
    state = Column(String(255))
    pincode = Column(Integer)

    phone: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(255))
