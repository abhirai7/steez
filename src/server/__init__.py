from __future__ import annotations

import os
import sqlite3
from typing import TYPE_CHECKING

import razorpay
from dotenv import load_dotenv
from flask import Flask, session
from flask_login import LoginManager, current_user

from src.user import User
from src.utils import sqlite_row_factory

load_dotenv()

RAZORPAY_KEY = os.getenv("RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")


if TYPE_CHECKING:
    assert isinstance(current_user, User)
    from src.type_hints import Client as RazorpayClient
else:
    RazorpayClient = razorpay.Client


login_manager = LoginManager()

with open("schema.sql") as f:
    schema = f.read()

app = Flask(__name__)
conn: sqlite3.Connection = sqlite3.connect("database.sqlite", check_same_thread=False)
conn.executescript(schema)

app.secret_key = f"{SECRET_KEY}"
login_manager.init_app(app)

conn.set_trace_callback(print)
conn.row_factory = sqlite_row_factory

razorpay_client: RazorpayClient = RazorpayClient(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
razorpay_client.set_app_details({"title": "SteezTM App", "version": "1.0"})

from .login_manager import *  # noqa
from .routes import *  # noqa
