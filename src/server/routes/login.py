from flask import redirect, render_template, url_for
from flask_login import current_user
from flask_security.forms import LoginForm
from flask_security.utils import login_user, logout_user

from src.server import app, db, security
from src.server.forms import RegisterForm


@app.route("/login", methods=["GET", "POST"])
def login_route():
    login: LoginForm = LoginForm()
    if login.validate_on_submit() and login.user:
        login_user(login.user)
        return redirect(url_for("home"))

    return render_template("login.html", login_user_form=login, current_user=current_user)


@app.route("/logout")
def logout():
    logout_user()

    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    register: RegisterForm = RegisterForm()

    if register.validate_on_submit() and isinstance(register, RegisterForm):
        if security.datastore.find_user(email=register.email.data, db=db):
            return render_template(
                "register.html",
                register_user_form=register,
                current_user=current_user,
                error="User already exists",
            )

        security.datastore.create_user(
            email=register.email.data,
            password=register.password.data,
            roles=["user"],
            db=db,
            #
            name=register.name.data,
            phone=register.phone.data,
            address=register.address.data,
            city=register.city.data,
            state=register.state.data,
            pincode=register.pincode.data,
        )
        db.session.commit()
        return redirect(url_for("login_route"))

    return render_template("register.html", register_user_form=register, current_user=current_user)
