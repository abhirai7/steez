from __future__ import annotations

import json

from flask_sqlalchemy import SQLAlchemy

with open(r".config.env.json") as f:
    config = json.load(f)

admins = config["admins"]


def ensure_admins(db: SQLAlchemy):
    for admin in admins:
        pass

    db.session.commit()
