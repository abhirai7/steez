from __future__ import annotations

from typing import TYPE_CHECKING

import arrow
from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required
from razorpay.errors import SignatureVerificationError

from src.favourite import Favourite
from src.order import Order
from src.product import Product
from src.server import RAZORPAY_KEY, app, conn, razorpay_client, sitemapper
from src.server.forms import (
    AddReviewForm,
    AddToCartForm,
    LoginForm,
    SearchForm,
    SubscribeNewsLetterForm,
    PaymentMethod,
)
from src.user import User
from src.utils import FAQ_DATA, format_number, get_product_pictures, size_chart

if TYPE_CHECKING:
    assert isinstance(current_user, User)


def product_ids():
    return [product.id for product in Product.all(conn)]


@sitemapper.include(
    url_variables={"product_id": product_ids()},
    lastmod=arrow.now().format("YYYY-MM-DD"),
    changefreq="daily",
)
@app.route("/products/<int:product_id>", methods=["GET"])
@app.route("/products/<int:product_id>/", methods=["GET"])
def product(product_id: int):
    product = Product.from_id(conn, product_id)
    pictures = get_product_pictures(product.unique_id)
    reviews = product.categorised_reviews

    cart_form: AddToCartForm = AddToCartForm(product)
    review_form: AddReviewForm = AddReviewForm()

    return render_template(
        "product.html",
        product=product,
        pictures=pictures,
        size_chart=[
            (size, data["CHEST"], data["LENGTH"]) for size, data in size_chart.items()
        ],
        current_user=current_user,
        form=cart_form,
        review_form=review_form,
        error=request.args.get("error"),
        arrow=arrow,
        FAQ=FAQ_DATA,
        reviews=reviews,
        search_form=SearchForm(),
        newsletter_form=SubscribeNewsLetterForm(),
        login_form=LoginForm(),
    )


@app.route("/products/<int:product_id>/add-to-cart", methods=["POST"])
@login_required
def add_to_cart(product_id: int):
    product = Product.from_id(conn, product_id)
    form: AddToCartForm = AddToCartForm()
    if form.validate_on_submit() and form.quantity.data:
        product = Product.from_size(conn, id=product.id, size=form.size.data)

        current_user.add_to_cart(product=product, quantity=int(form.quantity.data))

        return redirect(url_for("product", product_id=product_id))
    return redirect(url_for("product", product_id=product_id))


@app.route("/products/<int:product_id>/remove-from-cart", methods=["GET"])
@login_required
def remove_from_cart(product_id: int):
    product = Product.from_id(conn, product_id)
    current_user.remove_from_cart(product=product)

    return redirect(url_for("checkout"))


@app.route(
    "/products/<int:product_id>/add-review",
    methods=["POST"],
)
@login_required
def add_review(product_id: int):
    product = Product.from_id(conn, product_id)
    review_form: AddReviewForm = AddReviewForm()

    if (
        review_form.validate_on_submit()
        and request.method == "POST"
        and review_form.review.data
    ):
        current_user.add_review(
            product=product, review=review_form.review.data, stars=5
        )
        return redirect(url_for("product", product_id=product_id))
    return redirect(url_for("product", product_id=product_id))


@app.route("/products/<int:product_id>/is-favourite", methods=["GET"])
@app.route("/products/<int:product_id>/is-favourite/", methods=["GET"])
@login_required
def is_favourite(product_id: int):
    product = Product.from_id(conn, product_id)
    return {"is_favourite": Favourite.exists(conn, user=current_user, product=product)}


@app.route("/products/<int:product_id>/add-to-favourites", methods=["GET"])
@app.route("/products/<int:product_id>/add-to-favourites/", methods=["GET"])
@login_required
def add_to_favourites(product_id: int):
    product = Product.from_id(conn, product_id)
    current_user.add_to_fav(product=product)
    return redirect(url_for("product", product_id=product_id))


@app.route("/products/<int:product_id>/remove-from-favourites", methods=["GET"])
@app.route("/products/<int:product_id>/remove-from-favourites/", methods=["GET"])
@login_required
def remove_from_favourites(product_id: int):
    current_user.remove_from_fav(product=Product.from_id(conn, product_id))
    return redirect(url_for("product", product_id=product_id))


@app.route("/checkout")
@login_required
def checkout():
    return render_template(
        "checkout.html",
        current_user=current_user,
        format_number=format_number,
        newsletter_form=SubscribeNewsLetterForm(),
        search_form=SearchForm(),
        login_form=LoginForm(),
        checkout_form=PaymentMethod(),
    )


@app.route("/final-ckeckout", methods=["POST"])
@app.route("/final-ckeckout/", methods=["POST"])
@login_required
def final_checkout():
    form: PaymentMethod = PaymentMethod()

    if form.validate_on_submit():
        gift_code = (form.gift_card.data or "").replace(" ", "").upper()
        if form.method.data == "razorpay":
            order = current_user.full_checkout(razorpay_client, gift_code=gift_code)

            variables = {
                "razorpay_key": RAZORPAY_KEY,
                "amount": order["amount"],
                "order_id": order["id"],
                "giftcard": False,
            }
            return render_template("payment.html", **variables)
        else:
            current_user.partial_checkout(gift_code=gift_code)
            return redirect(url_for("order_history", limit=1))

    return redirect(url_for("checkout"))

@app.route("/razorpay-webhook/product", methods=["POST"])
@app.route("/razorpay-webhook/product/", methods=["POST"])
def razorpay_webhook():
    data = request.get_json()

    try:
        razorpay_client.utility.verify_payment_signature(data)
        order = Order.from_razorpay_order_id(conn, data["razorpay_order_id"])

        assert order.user.id == current_user.id

        order.update_order_status(
            status="PAID", razorpay_order_id=data["razorpay_order_id"]
        )
    except SignatureVerificationError:
        return {"status": "error"}, 400

    return {"status": "ok"}, 200


@app.route("/delete-order/<int:order_id>")
@login_required
def delete_order(order_id: int):
    Order.delete(conn, order_id=order_id, user_id=current_user.id)
    return redirect(url_for("order_history"))
