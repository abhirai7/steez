from __future__ import annotations

import os
import pathlib
import sqlite3
from typing import TYPE_CHECKING

import razorpay
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager, current_user
from flask_sitemapper import Sitemapper
from flask_wtf import CSRFProtect

from src.user import User
from src.utils import SQLITE_OLD, backup_sqlite_database, sqlite_row_factory

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
app.secret_key = f"{SECRET_KEY}"

schema = pathlib.Path("schema.sql").read_text()
conn: sqlite3.Connection = sqlite3.connect("database.sqlite", check_same_thread=False)
conn.executescript(schema)
conn.row_factory = sqlite_row_factory

login_manager = LoginManager()
csrf = CSRFProtect(app)
sitemapper = Sitemapper()

login_manager.init_app(app)
sitemapper.init_app(app)

razorpay_client: RazorpayClient = RazorpayClient(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
razorpay_client.set_app_details({"title": "SteezTM App", "version": "1.0"})

if SQLITE_OLD:
    app.logger.warning(
        "**SQLITE VERSION IS TOO OLD. PLEASE USE 3.35.0 OR NEWER. FEW FEATURES MAY NOT WORK.**"
    )

scheduler = BackgroundScheduler()

scheduler.add_job(
    backup_sqlite_database,
    "interval",
    seconds=5,
    args=(conn,),
)

scheduler.start()

from .filters import *  # noqa
from .login_manager import *  # noqa
from .routes import *  # noqa
