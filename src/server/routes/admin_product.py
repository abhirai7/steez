from flask import redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug import Response

from src.server import app, conn
from src.server.forms import ProductAddForm, ProductEditForm
from src.user import Admin
from src.product import Product
from src.user import User
from src.order import Order
import os

UPLOAD_FOLDER = "src/server/static/product_pictures"


@app.route("/admin/manage/product", methods=["GET", "POST"])
@login_required
def admin_manage_product():
    products = Product.all(conn)
    return render_template("admin_manage_product.html", products=products)


@app.route("/admin/manage/product/add", methods=["GET", "POST"])
@login_required
def admin_add_product():
    addform: ProductAddForm = ProductAddForm()

    if addform.validate_on_submit() and request.method == "POST":

        assert (
            addform.name.data and addform.price.data and addform.stock.data and addform.description.data 
        )

        product = Product.create(
            conn,
            name=addform.name.data,
            price=float(addform.price.data),
            stock=int(addform.stock.data),
            description=addform.description.data,
        )
        images = addform.images.data

        for image in images:
            if not os.path.exists(f"{UPLOAD_FOLDER}/{product.id}/"):
                os.makedirs(f"{UPLOAD_FOLDER}/{product.id}/")

            with open(f"{UPLOAD_FOLDER}/{product.id}/{image.filename}", "wb+") as f:
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


