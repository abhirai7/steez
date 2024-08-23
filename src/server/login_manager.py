from flask import redirect, url_for
from werkzeug import Response

from src.server import conn, login_manager
from src.user import User, Admin


@login_manager.user_loader
def load_user(user_id: int) -> User | None:
    user_id = int(user_id)

    try:
        if user_id == 1:
            return Admin.from_id(conn, user_id)

        usr = User.from_id(conn, user_id)
        return usr

    except ValueError:
        return None


@login_manager.unauthorized_handler
def unauthorized() -> Response:
    return redirect(url_for("login_route"))


@login_manager.request_loader
def load_user_from_request(request) -> User | None:
    email = request.form.get("email")
    password = request.form.get("password")

    if email and password:
        try:
            user = User.from_email(conn, email=email, password=password)
            return user
        except ValueError:
            return None

    return None
