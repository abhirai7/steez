from __future__ import annotations

import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert

with open(r".config.env.json") as f:
    config = json.load(f)

admins = config["admins"]


def ensure_admins(db: SQLAlchemy):
    from src.server.models import Users

    for admin in admins:
        if not db.session.query(Users).filter_by(EMAIL=admin["email"], ROLE="ADMIN").first():
            smt = insert(Users).values(
                NAME=admin["name"],
                EMAIL=admin["email"],
                PASSWORD=admin["password"],
                ROLE="ADMIN",
                PHONE=admin["phone"],
                ADDRESS=admin["address"],
            )
            db.session.execute(smt)

    db.session.commit()
