from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING

from flask import Request, render_template
from flask_login import current_user

from src.server import db, login_manager
from src.server.models import User as Users
from src.user import Admin, User

if TYPE_CHECKING:
    assert isinstance(current_user, User)

HTTP_UNAUTHORIZED = 403


@login_manager.user_loader
def load_user(user_id: str | int) -> User | None:
    user_id = int(user_id)

    user = Users.query.get(user_id)
    if user:
        if user.role == "ADMIN":
            admin = Admin(db, **{k.lower(): v for k, v in user.__dict__.items()})
            return admin

        return User(db, **{k.lower(): v for k, v in user.__dict__.items()})


@login_manager.request_loader
def load_user_from_request(request: Request) -> User | None:
    email = request.form.get("email") or request.args.get("email")
    password = request.form.get("password") or request.args.get("password")

    if email and password:
        try:
            return User.from_email(db, email=email, password=password)
        except ValueError:
            return None

    return None


def admin_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_admin:
            return func(*args, **kwargs)

        return render_template("error/403.html"), HTTP_UNAUTHORIZED

    return wrapper
