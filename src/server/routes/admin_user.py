from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

from src.server import app, conn
from src.user import User


@app.route("/admin/manage/user", methods=["GET", "POST"])
@login_required
def admin_manage_user():
    users = User.all(conn)
    return render_template("admin_manage_user.html", users=users)


@app.route("/admin/manage/user/delete", methods=["POST", "GET"])
@login_required
def admin_delete_user(id):
    current_user.delete_user(conn, id)
    return redirect(url_for("admin_manage_user"))
