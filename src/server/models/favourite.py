from __future__ import annotations

from sqlalchemy import VARCHAR, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.server import db

from .user import User


class Favourite(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id, ondelete="cascade"), nullable=False)  # type: ignore[valid-type]
    product_unique_id: Mapped[int] = mapped_column(VARCHAR(16), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "product_unique_id", name="unique_favorite"),)
