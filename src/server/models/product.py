from __future__ import annotations

from datetime import datetime

from sqlalchemy import DECIMAL, TEXT, TIMESTAMP, VARCHAR, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.server import db

from .category import Category


class Product(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unique_id: Mapped[str] = mapped_column(VARCHAR(16), nullable=False)
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    display_price: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=-1)
    size: Mapped[str] = mapped_column(TEXT, default=None)
    category: Mapped[int] = mapped_column(Integer, ForeignKey(Category.id, ondelete="CASCADE"), nullable=False)
    keywords: Mapped[str] = mapped_column(TEXT, default="")
    created_at: Mapped[int] = mapped_column(TIMESTAMP, default=datetime.now)
