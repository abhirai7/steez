from datetime import datetime

from sqlalchemy import (
    CHAR,
    DECIMAL,
    TEXT,
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
)

from src.server import db

from .product import Product
from .user import User

__all__ = ["Order"]


class Order(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)  # type: ignore[valid-type]
    product_id = Column(Integer, ForeignKey(Product.id, ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)
    status = Column(CHAR(4), default="PEND")
    razorpay_order_id = Column(TEXT, default=None)
    seen = Column(Boolean, default=False)
