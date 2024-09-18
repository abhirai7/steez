from __future__ import annotations

import arrow
from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from src.order import Order
from src.product import Product
from src.server import app, conn, razorpay_client, admin_login_required
from src.server.forms import AdminForm
from src.user import Admin, User


def todays_settlement(response: dict):
    today = arrow.now().format("YYYY-MM-DD")

    todays_settlements = [
        item
        for item in response["items"]
        if arrow.get(item["created_at"]).format("YYYY-MM-DD") == today
    ]

    return sum(item["amount"] for item in todays_settlements)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    form: AdminForm = AdminForm(conn)

    if form.validate_on_submit() and request.method == "POST":
        assert form.password.data

        admin = Admin.from_email(conn, password=form.password.data)
        login_user(admin)
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html", form=form, current_user=current_user)


@app.route("/admin/logout")
@admin_login_required
def admin_logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/admin/dashboard")
@app.route("/admin/dashboard/")
@admin_login_required
def admin_dashboard():
    assert current_user.is_admin

    product_count = Product.total_count(conn)
    user_count = User.total_count(conn)
    order_count = Order.total_count(conn)

    settlements = razorpay_client.settlement.all({"count": 100})

    return render_template(
        "admin_dashboard.html",
        product_count=product_count,
        user_count=user_count,
        order_count=order_count,
        current_user=current_user,
        settlements=settlements,
        todays_settlement=todays_settlement(settlements),
    )
