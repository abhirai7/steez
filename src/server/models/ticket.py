from __future__ import annotations

from datetime import datetime

from sqlalchemy import CHAR, TEXT, TIMESTAMP, Column, ForeignKey, Integer

from src.server import db

from .user import User


class Ticket(db.Model):

    id = Column(Integer, primary_key=True, autoincrement=True)
    replied_to = Column(Integer, ForeignKey("ticket.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)  # type: ignore[valid-type]
    subject = Column(TEXT, nullable=False)
    message = Column(TEXT, nullable=False)
    status = Column(CHAR(4), default="OPEN")
    created_at = Column(TIMESTAMP, default=datetime.now)
