from flask import render_template

from src.server import admin_login_required, app, db
from src.user import User


@app.route("/admin/manage/user", methods=["GET", "POST"])
@admin_login_required
def admin_manage_user():
    users = User.all(db)
    return render_template("admin/admin_manage_user.html", users=users)
