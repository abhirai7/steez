from flask import render_template
from flask_login import current_user, login_required

from src.product import Product
from src.server import app, conn
from src.utils import format_to_special


@app.route("/")
@app.route("/home/")
def home():
    products = Product.all(conn)
    return render_template(
        "front.html",
        format_to_special=format_to_special,
        products=products,
        current_user=current_user,
    )


@app.route("/search/<string:query>")
def search(query: str):
    products = Product.search(conn, query)
    return render_template(
        "front.html",
        format_to_special=format_to_special,
        products=products,
        current_user=current_user,
    )


@app.route("/refund-policy/")
@app.route("/refund-policy")
def refund_policy():
    return render_template("refund_policy.html")


@app.route("/order-history/")
@app.route("/order-history")
@login_required
def order_history():
    orders = current_user.orders
    return render_template("order_history.html", orders=orders, current_user=current_user)
