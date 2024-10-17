from __future__ import annotations

from flask_security.models import fsqla_v3 as fsqla

from src.server import db

__all__ = ["User"]


class User(db.Model, fsqla.FsUserMixin):
    pass
