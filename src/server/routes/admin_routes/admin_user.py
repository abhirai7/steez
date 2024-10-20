from flask import render_template
from flask_security.decorators import roles_required

from src.server import app, db
from src.user import User


@app.route("/admin/manage/user", methods=["GET", "POST"])
@roles_required("admin")
def admin_manage_user():
    users = User.all(db)
    return render_template("admin/admin_manage_user.html", users=users)
