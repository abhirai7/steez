from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import (
    EmailField,
    Field,
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
    TelField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from src.user import User


# fmt: off
class LoginForm(FlaskForm):
    email       = EmailField("Email address", validators=[DataRequired(), Email()])
    password    = PasswordField("Password", validators=[DataRequired(), Length(min=8)])

    submit      = SubmitField("Login")


class RegisterForm(FlaskForm):
    def __init__(self, db: SQLAlchemy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db

    name         = StringField("Person Details", validators=[DataRequired()], render_kw={"autocomplete": "off"})
    email        = EmailField("", validators=[DataRequired(), Email()], render_kw={"autocomplete": "off"})
    password     = PasswordField("", validators=[DataRequired(), Length(min=8)], render_kw={"autocomplete": "off"})
    confirm_password = PasswordField("", validators=[DataRequired(), EqualTo("password")], render_kw={"autocomplete": "off"})

    address_line1 = StringField("Address Details", validators=[DataRequired()], render_kw={"autocomplete": "off"})

    city         = StringField("", validators=[DataRequired()], render_kw={"autocomplete": "off"})
    state        = StringField("", validators=[DataRequired()], render_kw={"autocomplete": "off"})
    pincode      = IntegerField("", validators=[DataRequired()], render_kw={"autocomplete": "off"})
    phone        = TelField("", validators=[DataRequired()], render_kw={"autocomplete": "off"})

    submit       = SubmitField("Register")

    def validate_email(self, email: EmailField):
        assert email.data

        str_email = email.data.lower()

        if User.exists(self.db, email=str_email):
            raise ValidationError("Email already registered")

        return True

    def validate_phone(self, phone: IntegerField):
        return self._validate_integer(phone, 10, "Phone number must be 10 digits long")

    def validate_pincode(self, pincode: IntegerField):
        assert pincode.data

        return self._validate_integer(pincode, 6, "Pincode must be 6 digits long")

    def _validate_integer(self, field: Field, limit: int, error_message: str):
        phone_str = str(field.data)
        if len(phone_str) != limit:
            raise ValidationError(error_message)
        return True


class AdminForm(FlaskForm):
    def __init__(self, db: SQLAlchemy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db

    password    = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit      = SubmitField("Login")

# fmt: on
