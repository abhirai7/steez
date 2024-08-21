from flask import redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user

from src.server import app, conn
from src.server.forms import AdminForm
from src.user import Admin
from src.product import Product
from src.user import User
from src.order import Order



@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    form: AdminForm = AdminForm(conn)

    if form.validate_on_submit() and request.method == "POST":
        assert form.password.data

        admin = Admin.from_email(
            conn, password=form.password.data
        )
        login_user(admin)
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html", form=form, current_user=current_user)


@app.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/admin/dashboard")
@app.route("/admin/dashboard/")
@login_required
def admin_dashboard():
    assert current_user.is_admin
    products = Product.all(conn)
    users = User.all(conn)
    orders = Order.all(conn)

    return render_template("admin_dashboard.html", products=products, users=users, orders=orders, current_user=current_user)