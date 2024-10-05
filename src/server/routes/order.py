from __future__ import annotations

from typing import TYPE_CHECKING

from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required
from razorpay.errors import SignatureVerificationError

from src.order import Order
from src.server import RAZORPAY_KEY, app, conn, razorpay_client
from src.server.forms import LoginForm, PaymentMethod, SearchForm, SubscribeNewsLetterForm
from src.user import User
from src.utils import format_number

if TYPE_CHECKING:
    assert isinstance(current_user, User)


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
        elif form.method.data == "cash":
            current_user.partial_checkout(gift_code=gift_code, status="COD")
            return redirect(url_for("order_history"))

    return redirect(url_for("checkout"))


@app.route("/razorpay-webhook/product", methods=["POST"])
@app.route("/razorpay-webhook/product/", methods=["POST"])
def razorpay_webhook():
    data = request.get_json()

    try:
        razorpay_client.utility.verify_payment_signature(data)
        order = Order.from_razorpay_order_id(conn, data["razorpay_order_id"])

        assert order.user.id == current_user.id

        order.update_order_status(status="PAID", razorpay_order_id=data["razorpay_order_id"])
    except SignatureVerificationError:
        return {"status": "error"}, 400

    return {"status": "ok"}, 200


@app.route("/order-history/delete-order/<int:order_id>")
@login_required
def delete_order(order_id: int):
    Order.delete(conn, order_id=order_id, user_id=current_user.id)
    return redirect(url_for("order_history"))


@app.route("/order-history/pay-now/<string:razorpay_order_id>")
@app.route("/order-history/pay-now/<string:razorpay_order_id>/")
@login_required
def pay_now(razorpay_order_id: str):
    order = razorpay_client.order.fetch(razorpay_order_id)
    if not order:
        return redirect(url_for("order_history"))

    if order["status"] == "created":
        variables = {
            "razorpay_key": RAZORPAY_KEY,
            "amount": order["amount"],
            "order_id": order["id"],
            "giftcard": False,
        }
        return render_template("payment.html", **variables)

    return redirect(url_for("order_history"))
