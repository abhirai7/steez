from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint

from src.server import db

from .product import Product
from .user import User


class Cart(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)  # type: ignore[valid-type]
    product_id = Column(Integer, ForeignKey(Product.id, ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "product_id", name="unique_cart"),)
