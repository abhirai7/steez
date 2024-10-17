from __future__ import annotations

from datetime import datetime

from sqlalchemy import TEXT, TIMESTAMP, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.server import db

from .user import User


class GiftCard(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)  # type: ignore[valid-type]
    code: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[int] = mapped_column(TIMESTAMP, default=datetime.now)
    used_at: Mapped[int] = mapped_column(TIMESTAMP, default=None)
