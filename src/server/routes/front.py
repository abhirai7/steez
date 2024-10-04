from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import arrow
from flask import jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.carousel import Carousel
from src.product import Category, Product
from src.server import TODAY, app, conn, sitemapper
from src.server.forms import (
    AddToCartForm,
    GiftCardForm,
    LoginForm,
    SearchForm,
    SubscribeNewsLetterForm,
)
from src.utils import FAQ_DATA, newsletter_email_add_to_db

if TYPE_CHECKING:
    from src.user import User

    assert isinstance(current_user, User)


@sitemapper.include(lastmod=TODAY, changefreq="daily", priority=0.9)
@app.route("/")
def home():
    products = Product.all(conn, limit=6)
    categories = Product.categorise_products(products, limit=6)

    return render_template(
        "front.html",
        products=products,
        current_user=current_user,
        gift_form=GiftCardForm(),
        show_hero=True,
        form=AddToCartForm(),
        categories=categories,
        search_form=SearchForm(),
        newsletter_form=SubscribeNewsLetterForm(),
        carousels=Carousel.all(conn),
        login_form=LoginForm(),
    )


@sitemapper.include(lastmod=TODAY, changefreq="yearly", priority=0.5)
@app.route("/faq/")
@app.route("/faq")
def faq():
    return render_template(
        "faq.html",
        current_user=current_user,
        FAQ=FAQ_DATA,
        search_form=SearchForm(),
        categories=Category.all(conn),
        newsletter_form=SubscribeNewsLetterForm(),
        login_form=LoginForm(),
    )


@app.route("/search/", methods=["POST"])
@app.route("/search", methods=["POST"])
def search():
    form: SearchForm = SearchForm()

    query = request.args.get("query")

    if form.validate_on_submit() and form.query.data and request.method == "POST":
        query = form.query.data

    if not query:
        return redirect(url_for("home"))

    products = Product.search(conn, query)

    return render_template(
        "front_search.html",
        products=products,
        current_user=current_user,
        search_form=form,
        categories=Category.all(conn),
        newsletter_form=SubscribeNewsLetterForm(),
        login_form=LoginForm(),
    )


@lru_cache(maxsize=2**6)
def _autocomplete(*, query: str = "") -> list[Product]:
    if not query:
        return []
    print("cache didnt hit")
    return Product.search(conn, query=query)


@app.route("/autocomplete")
@app.route("/autocomplete/")
def autocomplete():
    query = request.args.get("q", "")
    products = _autocomplete(query=query)

    suggestions = [product.name.lower() for product in products]
    return jsonify(suggestions=suggestions)


@sitemapper.include(lastmod=TODAY, changefreq="monthly", priority=0.6)
@app.route("/refund-policy/")
@app.route("/refund-policy")
def refund_policy():
    return render_template(
        "refund_policy.html",
        search_form=SearchForm(),
        newsletter_form=SubscribeNewsLetterForm(),
        categories=Category.all(conn),
        login_form=LoginForm(),
    )


@app.route("/order-history/")
@app.route("/order-history")
@login_required
def order_history():
    orders = current_user.orders
    if limit := request.args.get("limit", 10):
        orders = orders[: int(limit)]

    return render_template(
        "order_history.html",
        orders=orders,
        current_user=current_user,
        arrow=arrow,
        search_form=SearchForm(),
        newsletter_form=SubscribeNewsLetterForm(),
        categories=Category.all(conn),
        login_form=LoginForm(),
    )


@app.route("/contact-us/")
@app.route("/contact-us")
def contact_us():
    return render_template(
        "contact_us.html",
        current_user=current_user,
        newsletter_form=SubscribeNewsLetterForm(),
        login_form=LoginForm(),
        search_form=SearchForm(),
    )


@app.route("/about-us/")
@app.route("/about-us")
def about_us():
    return render_template(
        "about_us.html",
        current_user=current_user,
        newsletter_form=SubscribeNewsLetterForm(),
        login_form=LoginForm(),
        search_form=SearchForm(),
    )


@app.route("/subscribe", methods=["POST"])
@app.route("/subscribe/", methods=["POST"])
def subscribe():
    form: SubscribeNewsLetterForm = SubscribeNewsLetterForm()

    if form.validate_on_submit() and form.email.data:
        email = form.email.data
        newsletter_email_add_to_db(conn, email=email)

    return redirect(url_for("home"))


for category in Category.all(conn):

    def category_page(category=category):
        products = Product.get_by_category(conn, category=category)
        return render_template(
            "front_search.html",
            products=products,
            category=category,
            current_user=current_user,
            search_form=SearchForm(),
            newsletter_form=SubscribeNewsLetterForm(),
            categories=Category.all(conn),
            login_form=LoginForm(),
        )

    app.add_url_rule(
        f"/category/{category.name.lower().replace(' ', '-')}",
        f"category_{category.name.lower().replace(' ', '_')}",
        category_page,
    )
