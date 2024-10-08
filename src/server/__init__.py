from __future__ import annotations

import os
from typing import TYPE_CHECKING

import razorpay
from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sitemapper import Sitemapper
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from src.user import User

load_dotenv()

RAZORPAY_KEY = os.getenv("RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")


if TYPE_CHECKING:
    assert isinstance(current_user, User)
    from src.type_hints import Client as RazorpayClient
else:
    RazorpayClient = razorpay.Client

TODAY = "2024-09-15"

app = Flask(__name__)
app.config["SECRET_KEY"] = f"{SECRET_KEY}"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite"

login_manager = LoginManager(app)
sitemapper = Sitemapper(app, https=True)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

razorpay_client: RazorpayClient = RazorpayClient(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
razorpay_client.set_app_details({"title": "SteezTM App", "version": "1.0"})

from .models import *  # noqa

with app.app_context():
    db.engine.echo = True

    db.create_all()

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

from .filters import *  # noqa
from .login_manager import *  # noqa
from .routes import *  # noqa
