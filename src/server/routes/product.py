from __future__ import annotations

from typing import TYPE_CHECKING

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from razorpay.errors import SignatureVerificationError

from src.order import Order
from src.product import Product
from src.server import RAZORPAY_KEY, app, conn, razorpay_client
from src.server.forms import AddReviewForm, AddToCartForm
from src.user import User
from src.utils import format_number, format_to_special, get_product_pictures, size_chart

if TYPE_CHECKING:
    assert isinstance(current_user, User)


@app.route("/products/<int:product_id>", methods=["GET", "POST"])
@app.route("/products/<int:product_id>/", methods=["GET", "POST"])
def product(product_id: int):
    product = Product.from_id(conn, product_id)
    pictures = get_product_pictures(product.unique_id)

    _products = Product.from_unique_id(conn, product.unique_id)

    cart_form: AddToCartForm = AddToCartForm()
    review_form: AddReviewForm = AddReviewForm()

    return render_template(
        "product.html",
        product=product,
        pictures=pictures,
        format_to_special=format_to_special,
        size_chart=[
            (size, data["CHEST"], data["LENGTH"]) for size, data in size_chart.items()
        ],
        current_user=current_user,
        form=cart_form,
        review_form=review_form,
        error=request.args.get("error"),
    )


@app.route("/products/<int:product_id>/add-to-cart", methods=["POST"])
@login_required
def add_to_cart(product_id: int):
    product = Product.from_id(conn, product_id)
    form: AddToCartForm = AddToCartForm()

    if form.validate_on_submit() and request.method == "POST" and form.quantity.data and form.size.data:
        try:
            products = product.from_unique_id(conn, product.unique_id, size=form.size.data)
            if not products:
                return redirect(url_for("product", product_id=product_id, error="Item not available"))

            current_user.add_to_cart(product=products[0], quantity=form.quantity.data)
        except ValueError as e:
            flash(str(e), "error")

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


@app.route("/checkout")
@login_required
def checkout():
    return render_template(
        "checkout.html", current_user=current_user, format_number=format_number
    )


@app.route("/final-ckeckout")
@login_required
def final_checkout():
    order = current_user.full_checkout(razorpay_client)

    variables = {
        "razorpay_key": RAZORPAY_KEY,
        "amount": order["amount"],
        "order_id": order["id"],
        "giftcard": False,
    }
    return render_template("payment.html", **variables)


@app.route("/razorpay-webhook-product", methods=["POST"])
@app.route("/razorpay-webhook-product/", methods=["POST"])
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


@app.route("/payment-success")
def payment_success():
    return render_template("payment_status.html", status="ok")


@app.route("/payment-failure")
def payment_failure():
    return render_template("payment_status.html", status="error")


@app.route("/delete-order/<int:order_id>")
@login_required
def delete_order(order_id: int):
    Order.delete(conn, order_id=order_id, user_id=current_user.id)
    return redirect(url_for("order_history"))
