from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING

from flask import Request, redirect, url_for
from flask_login import current_user
from werkzeug import Response

from src.server import conn, login_manager
from src.user import Admin, User

if TYPE_CHECKING:
    assert isinstance(current_user, User)

ADMIN_ID = 1
HTTP_UNAUTHORIZED = 403


@login_manager.user_loader
def load_user(user_id: str | int) -> User | None:
    user_id = int(user_id)

    try:
        if user_id == ADMIN_ID:
            return Admin.from_id(conn, user_id)

        return User.from_id(conn, user_id)
    except ValueError:
        return None


@login_manager.unauthorized_handler
def unauthorized() -> Response:
    return redirect(url_for("login_route"))


@login_manager.request_loader
def load_user_from_request(request: Request) -> User | None:
    email = request.form.get("email") or request.args.get("email")
    password = request.form.get("password") or request.args.get("password")

    if email and password:
        try:
            return User.from_email(conn, email=email, password=password)
        except ValueError:
            return None

    return None


def admin_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_admin:
            return func(*args, **kwargs)

        return redirect(url_for("login_route")), HTTP_UNAUTHORIZED

    return wrapper
