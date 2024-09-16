from __future__ import annotations

from typing import TYPE_CHECKING

import arrow
from flask import render_template
from flask_login import current_user, login_required

from src.product import Product
from src.server import TODAY, app, conn, sitemapper
from src.server.forms import GiftCardForm
from src.utils import FAQ_DATA, format_to_special

if TYPE_CHECKING:
    from src.user import User

    assert isinstance(current_user, User)


@sitemapper.include(lastmod=TODAY, changefreq="daily", priority=0.9)
@app.route("/")
@app.route("/home/")
def home():
    products = Product.all(conn)
    gift_form: GiftCardForm = GiftCardForm()

    return render_template(
        "front.html",
        format_to_special=format_to_special,
        products=products,
        current_user=current_user,
        gift_form=gift_form,
        show_hero=True,
    )


@sitemapper.include(lastmod=TODAY, changefreq="yearly", priority=0.5)
@app.route("/faq/")
@app.route("/faq")
def faq():
    return render_template("faq.html", current_user=current_user, FAQ=FAQ_DATA)


@app.route("/search/<string:query>", methods=["GET"])
def search(query: str):
    products = Product.search(conn, query)
    gift_form: GiftCardForm = GiftCardForm()
    return render_template(
        "front.html",
        format_to_special=format_to_special,
        products=products,
        current_user=current_user,
        gift_form=gift_form,
        show_hero=False,
    )


@sitemapper.include(lastmod=TODAY, changefreq="monthly", priority=0.6)
@app.route("/refund-policy/")
@app.route("/refund-policy")
def refund_policy():
    return render_template("refund_policy.html")


@app.route("/order-history/")
@app.route("/order-history")
@login_required
def order_history():
    orders = current_user.orders
    return render_template(
        "order_history.html", orders=orders, current_user=current_user, arrow=arrow
    )
