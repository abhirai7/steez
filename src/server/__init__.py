from __future__ import annotations

import os
from typing import TYPE_CHECKING

import razorpay
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager, current_user
from flask_mailman import Mail
from flask_migrate import Migrate
from flask_security.core import Security
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.models import fsqla_v3 as fsqla
from flask_security.utils import hash_password
from flask_sitemapper import Sitemapper
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from src.server.forms import RegisterForm
from src.user import User

load_dotenv()

RAZORPAY_KEY = os.getenv("RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")
SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")

ADMIN_EMAIL = os.environ["ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

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
app.config["SECURITY_LOGIN_USER_TEMPLATE"] = "login.html"
app.config["SECURITY_TRACKABLE"] = True
app.config["SECURITY_REGISTERABLE"] = True
app.config["SECURITY_UNAUTHORIZED_VIEW"] = "/login"

app.config["SECURITY_REGISTER_URL"] = "/register"
app.config["SECURITY_REGISTER_USER_TEMPLATE"] = "register.html"
app.config["SECURITY_POST_REGISTER_VIEW"] = "/login"
app.config["SECURITY_USERNAME_REQUIRED"] = False

app.config["SECURITY_CSRF_COOKIE_NAME"] = "CSRF-Cookie"
app.config["SECURITY_DEFAULT_REMEMBER_ME"] = True
app.config["MAIL_SERVER"] = os.environ["MAIL_SERVER"]
app.config["MAIL_PORT"] = os.environ["MAIL_PORT"]
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["SECURITY_EMAIL_SENDER"] = os.environ["DEFAULT_MAIL_SENDER"].split(",")[-1]
app.config["SECURITY_EMAIL_VALIDATOR_ARGS"] = {"check_deliverability": False}

login_manager = LoginManager(app)
sitemapper = Sitemapper(app, https=True)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)
mail = Mail(app)

razorpay_client: RazorpayClient = RazorpayClient(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
razorpay_client.set_app_details({"title": "SteezTM App", "version": "1.0"})

fsqla.FsModels.set_db_info(db)

from .models import Role  # noqa
from .models import __models__  # noqa
from .models import User as DBUser  # noqa

user_datastore = SQLAlchemyUserDatastore(db, DBUser, Role)

security = Security(app, user_datastore, register_form=RegisterForm)

with app.app_context():
    db.engine.echo = True
    db.create_all()

    security.datastore.find_or_create_role(name="admin", description="Administrator")
    security.datastore.find_or_create_role(name="user", description="User")

    if not security.datastore.find_user(email=ADMIN_EMAIL):
        user = security.datastore.create_user(
            email=ADMIN_EMAIL,
            name="STEEZ-TM ADMIN",
            password=hash_password(ADMIN_PASSWORD),
            roles=["admin"],
        )
    db.session.commit()

app.jinja_env.autoescape = True
app.jinja_env.auto_reload = True

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

from .filters import *  # noqa
from .routes import *  # noqa
