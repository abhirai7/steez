from __future__ import annotations

from flask import redirect, render_template, url_for
from flask_login import current_user
from flask_security.decorators import roles_required

from src.product import GiftCard
from src.server import app, db
from src.server.forms import GiftCardForm


@app.route("/admin/giftcards")
@roles_required("admin")
def admin_giftcards():
    gift_cards = GiftCard.all(db)
    form = GiftCardForm()
    return render_template("admin/admin_manage_giftcard.html", gift_cards=gift_cards, form=form)


@app.route("/admin/giftcards/add", methods=["POST"])
@roles_required("admin")
def admin_giftcard_add():
    form: GiftCardForm = GiftCardForm()

    if form.validate_on_submit() and form.amount.data and int(form.amount.data) > 0:
        GiftCard.admin_create(db, user=current_user, amount=form.amount.data)

    return redirect(url_for("admin_giftcards"))
