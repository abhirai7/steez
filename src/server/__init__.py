from __future__ import annotations

import os
from typing import TYPE_CHECKING

import razorpay
from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_security.core import Security
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.models import fsqla_v3 as fsqla
from flask_sitemapper import Sitemapper
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from src.user import User

from .ensure_admins import ensure_admins

load_dotenv()

RAZORPAY_KEY = os.getenv("RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")
SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")

if TYPE_CHECKING:
    assert isinstance(current_user, User)
    from src.type_hints import Client as RazorpayClient
else:
    RazorpayClient = razorpay.Client

TODAY = "2024-09-15"

app = Flask(__name__)
app.config["SECRET_KEY"] = f"{SECRET_KEY}"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
app.config["SECURITY_PASSWORD_SALT"] = f"{SECURITY_PASSWORD_SALT}"
app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SAMESITE"] = "strict"
# app.config["SECURITY_LOGIN_USER_TEMPLATE"] = "login.html"

app.config["MAIL_SERVER"] = "smtp.google.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

login_manager = LoginManager(app)
sitemapper = Sitemapper(app, https=True)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

razorpay_client: RazorpayClient = RazorpayClient(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
razorpay_client.set_app_details({"title": "SteezTM App", "version": "1.0"})
fsqla.FsModels.set_db_info(db)

from .models import __models__  # noqa; noqa
from .models import Role, User

user_datastore = SQLAlchemyUserDatastore(db, User, Role)

security = Security(app, user_datastore)
with app.app_context():
    db.engine.echo = True

    for model in __models__:
        model.__table__.create(db.engine, checkfirst=True)
    ensure_admins(db)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

from .filters import *  # noqa
from .login_manager import *  # noqa
from .routes import *  # noqa
