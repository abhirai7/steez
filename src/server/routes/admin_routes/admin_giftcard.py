from __future__ import annotations

from flask import render_template

from src.product import GiftCard
from src.server import admin_login_required, app, conn


@app.route("/admin/giftcards")
@admin_login_required
def admin_giftcards():
    gift_cards = GiftCard.all(conn)
    return render_template("admin_manage_giftcard.html", gift_cards=gift_cards)
