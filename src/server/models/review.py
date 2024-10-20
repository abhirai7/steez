from datetime import datetime

from sqlalchemy import TIMESTAMP, VARCHAR, Column, ForeignKey, Integer

from src.server import db

from .product import Product
from .user import User


class Review(db.Model):
    db = db

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)  # type: ignore[valid-type]
    product_id = Column(Integer, ForeignKey(Product.id, ondelete="CASCADE"), nullable=False)
    stars = Column(Integer, nullable=False)
    review = Column(VARCHAR(255), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)
