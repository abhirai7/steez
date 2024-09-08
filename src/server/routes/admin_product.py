from __future__ import annotations

import os
import random
import string

from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.order import Order
from src.product import Product
from src.server import app, conn
import markdown

from src.server.forms import ProductAddForm

UPLOAD_FOLDER = "src/server/static/product_pictures"


def generate_unique_identifier():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=16))


@app.route("/admin/manage/product", methods=["GET", "POST"])
@login_required
def admin_manage_product():
    products = Product.all(conn, admin=True)
    return render_template("admin_manage_product.html", products=products)


@app.route("/admin/manage/product/add", methods=["GET", "POST"])
@login_required
def admin_add_product():
    addform: ProductAddForm = ProductAddForm()

    if addform.validate_on_submit() and request.method == "POST":
        assert (
            addform.name.data
            and addform.price.data
            and addform.stock.data
            and addform.description.data
            and addform.sizes.data
        )

        _id = generate_unique_identifier()

        for size in addform.sizes.data:
            product = Product.create(
                conn,
                name=addform.name.data,
                unique_id=_id,
                price=float(addform.price.data),
                stock=int(addform.stock.data),
                description=markdown.markdown(addform.description.data),
                size=size,
            )

        images = addform.images.data

        for image in images:
            if not os.path.exists(f"{UPLOAD_FOLDER}/{product.unique_id}/"):
                os.makedirs(f"{UPLOAD_FOLDER}/{product.unique_id}/")

            with open(
                f"{UPLOAD_FOLDER}/{product.unique_id}/{image.filename}", "wb+"
            ) as f:
                f.write(image.read())

        return redirect(url_for("admin_manage_product"))
    return render_template("admin_add_product.html", form=addform)


@app.route("/admin/manage/product/edit/<int:id>", methods=["GET", "POST"])
@login_required
def admin_edit_product(id):
    return redirect(url_for("admin_manage_product"))


@app.route("/admin/manage/product/delete/<int:id>", methods=["GET", "POST"])
@login_required
def admin_delete_product(id):
    current_user.delete_product(conn, id)

    return redirect(url_for("admin_manage_product"))


@app.route("/admin/manage/order", methods=["GET"])
@login_required
def admin_manage_order():
    orders = Order.all(conn)
    return render_template("admin_manage_order.html", orders=orders)
