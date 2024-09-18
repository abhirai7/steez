from flask import redirect, render_template, request, url_for

from src.product import Category
from src.server import admin_login_required, app, conn
from src.server.forms import CategoryAddForm


@app.route("/admin/manage/category", methods=["GET"])
@admin_login_required
def admin_manage_category():
    categories = Category.all(conn)
    addform: CategoryAddForm = CategoryAddForm()
    return render_template(
        "admin_manage_category.html", categories=categories, form=addform
    )


@app.route("/admin/manage/category/add", methods=["POST"])
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


@app.route("/admin/manage/category/delete/<int:id>", methods=["GET"])
@admin_login_required
def admin_delete_category(id):
    category = Category.from_id(conn, id)
    category.delete()
    return redirect(url_for("admin_manage_category"))
