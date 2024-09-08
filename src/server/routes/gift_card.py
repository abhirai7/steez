from __future__ import annotations

from typing import TYPE_CHECKING

import arrow
from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required
from razorpay.errors import SignatureVerificationError

from src.product import GiftCard
from src.server import RAZORPAY_KEY, app, conn, razorpay_client
from src.server.forms import GiftCardForm

if TYPE_CHECKING:
    from src.type_hints import RazorPayOrderDict
    from src.user import User

    assert isinstance(current_user, User)


@app.route("/buy-gift-card/", methods=["POST"])
@app.route("/buy-gift-card", methods=["POST"])
@login_required
def buy_gift_card():
    gift_form: GiftCardForm = GiftCardForm()
    if (
        gift_form.validate_on_submit()
        and gift_form.amount.data
        and int(gift_form.amount.data) > 0
    ):
        order = current_user.full_checkout_giftcard(
            razorpay_client=razorpay_client, amount=gift_form.amount.data
        )

        variables = {
            "razorpay_key": RAZORPAY_KEY,
            "amount": order["amount"],
            "order_id": order["id"],
            "description": "Payment - Gift Card",
            "webhook": "razorpay_webhook_giftcard",
            "giftcard": True,
        }
        return render_template("payment.html", **variables)
    return render_template("buy_gift_card.html", form=gift_form)


@app.route("/razorpay-webhook-giftcard", methods=["POST"])
@app.route("/razorpay-webhook-giftcard/", methods=["POST"])
def razorpay_webhook_giftcard():
    data = request.get_json()

    try:
        razorpay_client.utility.verify_payment_signature(data)
        order: RazorPayOrderDict = razorpay_client.order.fetch(
            data["razorpay_order_id"]
        )
        amount = int(order["amount"])

        gift = current_user._buy_gift_card(amount=int(amount / 100))
    except SignatureVerificationError:
        return {"status": "error"}, 400

    return {"status": "ok", "gift_card_code": gift.code}, 200


@app.route("/show-gift-card/")
@app.route("/show-gift-card")
@login_required
def show_gift_card():
    args = request.args
    code = args.get("gift_card_code")

    if code is None:
        return redirect(url_for("home"))

    try:
        if gift_card := GiftCard.exists(conn, code=code):
            return render_template(
                "show_gift_card.html", gift_card=gift_card, arrow=arrow
            )
    except ValueError:
        pass

    return redirect(url_for("home"))
