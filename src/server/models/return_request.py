from datetime import datetime

from sqlalchemy import TEXT, TIMESTAMP, Column, ForeignKey, Integer

from src.server import db

from .order import Order


class ReturnRequest(db.Model):
    db = db

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey(Order.id, ondelete="CASCADE"), nullable=False)
    reason = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)
