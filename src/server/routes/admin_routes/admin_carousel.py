from __future__ import annotations

import os
import random
import string

from flask import redirect, render_template, url_for
from flask_security.decorators import roles_required

from src.carousel import Carousel
from src.server import app, db
from src.server.forms import CarouselForm

UPLOAD_FOLDER = "src/server/static/product_pictures"


def generate_unique_identifier():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=16))


@app.route("/admin/manage/carousel")
@roles_required("admin")
def admin_manage_carousel():
    form = CarouselForm()
    carousels = Carousel.all(db)
    return render_template("admin/admin_manage_carousel.html", form=form, carousels=carousels)


@app.route("/admin/delete/carousel/<int:id>")
@roles_required("admin")
def admin_delete_carousel(id):
    carousel = Carousel.get(db, id)
    carousel.delete()
    return redirect(url_for("admin_manage_carousel"))


@app.route("/admin/manage/carousel/add", methods=["POST"])
@roles_required("admin")
def admin_add_carousel():
    form: CarouselForm = CarouselForm()

    if form.validate_on_submit():
        assert form.image.data and form.heading.data and form.description.data

        image = form.image.data
        filename = image.filename
        _id = generate_unique_identifier()

        if not os.path.exists(f"{UPLOAD_FOLDER}/{_id}/"):
            os.makedirs(f"{UPLOAD_FOLDER}/{_id}/")

        with open(f"{UPLOAD_FOLDER}/{_id}/{filename}", "wb+") as f:
            f.write(image.read())

        Carousel.create(
            db,
            image=_id,
            heading=form.heading.data,
            description=form.description.data,
        )

    return redirect(url_for("admin_manage_carousel"))
