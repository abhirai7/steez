from __future__ import annotations

from typing import TYPE_CHECKING

from flask import redirect, url_for
from flask_login import current_user, login_required

from src.server import app, conn
from src.server.forms import TicketForm
from src.ticket import Ticket

if TYPE_CHECKING:
    from src.user import User

    assert isinstance(current_user, User)


@app.route("/contact-us/create-ticket/", methods=["POST"])
@app.route("/contact-us/create-ticket", methods=["POST"])
@login_required
def create_ticket():
    form: TicketForm = TicketForm()
    if form.validate_on_submit() and form.subject.data and form.message.data:
        Ticket.create(
            conn,
            user=current_user,
            replied_to=None,
            subject=form.subject.data,
            message=form.message.data,
        )
        return redirect(url_for("contact_us"))
    return redirect(url_for("contact_us"))
