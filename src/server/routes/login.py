from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from src.server import app, conn, sitemapper
from src.server.forms import LoginForm, RegisterForm
from src.user import User


@sitemapper.include()
@app.route("/login", methods=["GET", "POST"])
@app.route("/login/", methods=["GET", "POST"])
def login_route():
    login: LoginForm = LoginForm()

    if login.validate_on_submit() and request.method == "POST":
        assert login.email.data and login.password.data

        try:
            user = User.from_email(conn, email=login.email.data, password=login.password.data)
        except ValueError:
            redirect(url_for("home"))

        login_user(user)
        return redirect(url_for("home"))

    return render_template("login.html", form=login, current_user=current_user)


@app.route("/logout")
@app.route("/logout/")
@login_required
def logout():
    logout_user()

    return redirect(url_for("home"))


@sitemapper.include()
@app.route("/register", methods=["GET", "POST"])
@app.route("/register/", methods=["GET", "POST"])
def register():
    register: RegisterForm = RegisterForm(conn)

    if register.validate_on_submit() and request.method == "POST":
        assert register.email.data and register.password.data and register.name.data and register.phone.data

        address = f"{register.address_line1.data}".strip()
        address += f", {register.city.data}, {register.state.data}, {register.pincode.data}"

        User.create(
            conn,
            name=register.name.data,
            email=register.email.data,
            password=register.password.data,
            address=address,
            phone=str(register.phone.data),
        )

        return redirect(url_for("login_route"))

    return render_template("register.html", form=register)
