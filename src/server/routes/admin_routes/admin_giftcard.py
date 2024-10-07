from __future__ import annotations

from typing import TYPE_CHECKING

from flask import redirect, render_template, url_for
from flask_login import current_user

from src.product import GiftCard
from src.server import admin_login_required, app, db
from src.server.forms import GiftCardForm

if TYPE_CHECKING:
    from src.user import Admin

    assert isinstance(current_user, Admin)


@app.route("/admin/giftcards")
@admin_login_required
def admin_giftcards():
    gift_cards = GiftCard.all(db)
    form = GiftCardForm()
    return render_template("admin/admin_manage_giftcard.html", gift_cards=gift_cards, form=form)


@app.route("/admin/giftcards/add", methods=["POST"])
@admin_login_required
def admin_giftcard_add():
    form: GiftCardForm = GiftCardForm()

    if form.validate_on_submit() and form.amount.data and int(form.amount.data) > 0:
        GiftCard.admin_create(db, user=current_user, amount=form.amount.data)

    return redirect(url_for("admin_giftcards"))
