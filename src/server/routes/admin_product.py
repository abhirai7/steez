from __future__ import annotations

import json
import os
import random
import string

import markdown
from flask import redirect, render_template, request, url_for
from flask_login import current_user

from src.carousel import Carousel
from src.order import Order
from src.product import Category, GiftCard, Product
from src.server import app, conn, razorpay_client, admin_login_required
from src.server.forms import CarouselForm, CategoryAddForm, ProductAddForm
from src.utils import size_names

UPLOAD_FOLDER = "src/server/static/product_pictures"


def generate_unique_identifier():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=16))


@app.route("/admin/manage/product", methods=["GET", "POST"])
@admin_login_required
def admin_manage_product():
    page = max(int(request.args.get("page", 1)), 1)
    limit = int(request.args.get("limit", 15))
    skip = (page - 1) * limit
    products = Product.all(conn, admin=True, limit=limit, offset=skip)
    addform: ProductAddForm = ProductAddForm(conn)
    return render_template(
        "admin_manage_product.html",
        products=products,
        size_names=size_names,
        form=addform,
        page=page,
        limit=limit,
        skip=skip,
    )


@app.route("/admin/manage/product/add", methods=["GET", "POST"])
@admin_login_required
def admin_add_product():
    addform: ProductAddForm = ProductAddForm(conn)

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
                category=addform.category.data,
                display_price=addform.display_price.data or addform.price.data,
                keywords=addform.keywords.data or "",
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


@app.route("/admin/manage/category", methods=["GET"])
@admin_login_required
def admin_manage_category():
    categories = Category.all(conn)
    addform: CategoryAddForm = CategoryAddForm()
    return render_template(
        "admin_manage_category.html", categories=categories, form=addform
    )


@app.route("/admin/manage/category/add", methods=["GET", "POST"])
@admin_login_required
def admin_add_category():
    addform: CategoryAddForm = CategoryAddForm()

    if addform.validate_on_submit() and request.method == "POST":
        assert addform.name.data and addform.description.data

        Category.create(
            conn, name=addform.name.data, description=addform.description.data
        )

        return redirect(url_for("admin_manage_category"))
    return render_template("admin_manage_category.html", form=addform)


@app.route("/admin/manage/product/edit/<int:id>", methods=["GET", "POST"])
@admin_login_required
def admin_edit_product(id):
    return redirect(url_for("admin_manage_product"))


@app.route("/admin/manage/product/delete/<int:id>", methods=["GET", "POST"])
@admin_login_required
def admin_delete_product(id):
    current_user.delete_product(conn, id)

    return redirect(url_for("admin_manage_product"))


@app.route("/admin/manage/razorpay-orders", methods=["GET"])
@admin_login_required
def admin_manage_razorpay_order():
    page = max(int(request.args.get("page", 1)), 1)
    limit = int(request.args.get("limit", 15))
    skip = (page - 1) * limit

    response = razorpay_client.order.all({"count": limit, "skip": skip})

    total_order_amount = sum(item["amount"] for item in response["items"])
    total_paid = sum(
        item["amount_paid"] for item in response["items"] if item["amount_paid"]
    )
    total_due = sum(item["amount_due"] for item in response["items"])

    return render_template(
        "admin_manage_order.html",
        total_order_amount=total_order_amount,
        total_paid=total_paid,
        total_due=total_due,
        response=response,
        skip=skip,
        page=page,
        limit=limit,
        json=json,
    )


@app.route("/admin/manage/orders", methods=["GET"])
@admin_login_required
def admin_manage_order():
    page = max(int(request.args.get("page", 1)), 1)
    limit = int(request.args.get("limit", 15))
    skip = (page - 1) * limit

    orders = Order.all(conn, limit=limit, offset=skip)

    return render_template(
        "admin_manage_partial_order.html",
        orders=orders,
        page=page,
        skip=skip,
        limit=limit,
    )


@app.route("/admin/payouts", methods=["GET"])
@admin_login_required
def admin_payments():
    page = max(int(request.args.get("page", 1)), 1)
    limit = int(request.args.get("limit", 15))
    skip = (page - 1) * limit

    payments = razorpay_client.payment.all({"count": limit, "skip": skip})

    return render_template(
        "admin_payments.html", payments=payments, page=page, skip=skip, limit=limit
    )


@app.route("/admin/giftcards")
@admin_login_required
def admin_giftcards():
    gift_cards = GiftCard.all(conn)
    return render_template("admin_manage_giftcard.html", gift_cards=gift_cards)


@app.route("/admin/manage/carousel")
@admin_login_required
def admin_manage_carousel():
    form = CarouselForm()
    carousels = Carousel.all(conn)
    return render_template("admin_manage_carousel.html", form=form, carousels=carousels)


@app.route("/admin/delete/carousel/<int:id>")
@admin_login_required
def admin_delete_carousel(id):
    carousel = Carousel.get(conn, id)
    carousel.delete()
    return redirect(url_for("admin_manage_carousel"))


@app.route("/admin/manage/carousel/add", methods=["POST"])
@admin_login_required
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
            conn,
            image=_id,
            heading=form.heading.data,
            description=form.description.data,
        )

    return redirect(url_for("admin_manage_carousel"))
