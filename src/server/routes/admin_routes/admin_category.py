from flask import redirect, render_template, request, url_for
from flask_security.decorators import roles_required

from src.product import Category
from src.server import app, db
from src.server.forms import CategoryAddForm


@app.route("/admin/manage/category", methods=["GET"])
@roles_required("admin")
def admin_manage_category():
    categories = Category.all(db)
    addform: CategoryAddForm = CategoryAddForm()
    return render_template("admin/admin_manage_category.html", categories=categories, form=addform)


@app.route("/admin/manage/category/add", methods=["POST"])
@roles_required("admin")
def admin_add_category():
    addform: CategoryAddForm = CategoryAddForm()

    if addform.validate_on_submit() and request.method == "POST":
        assert addform.name.data and addform.description.data

        Category.create(db, name=addform.name.data, description=addform.description.data)

        return redirect(url_for("admin_manage_category"))
    return render_template("admin/admin_manage_category.html", form=addform)


@app.route("/admin/manage/category/delete/<int:id>", methods=["GET"])
@roles_required("admin")
def admin_delete_category(id):
    category = Category.from_id(db, id)
    category.delete()
    return redirect(url_for("admin_manage_category"))
