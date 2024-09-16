from flask import render_template
from flask_login import login_required

from src.server import app, conn
from src.user import User


@app.route("/admin/manage/user", methods=["GET", "POST"])
@login_required
def admin_manage_user():
    users = User.all(conn)
    return render_template("admin_manage_user.html", users=users)
