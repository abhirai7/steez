from __future__ import annotations

import sqlite3

from flask_wtf import FlaskForm
from wtforms import (
    EmailField,
    Field,
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from src.user import User


class LoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])

    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    def __init__(self, connection: sqlite3.Connection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = connection

    name: StringField = StringField("Person Details", validators=[DataRequired()])
    email = EmailField("", validators=[DataRequired(), Email()])
    password = PasswordField("", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "", validators=[DataRequired(), EqualTo("password")]
    )

    address_line1 = StringField("Address Details", validators=[DataRequired()])

    city = StringField("", validators=[DataRequired()])
    state = StringField("", validators=[DataRequired()])
    pincode = IntegerField("", validators=[DataRequired()])
    phone = IntegerField("", validators=[DataRequired()])

    submit = SubmitField("Register")

    def validate_email(self, email: EmailField):
        assert email.data

        str_email = email.data.lower()

        if User.exists(self.conn, email=str_email):
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
    def __init__(self, connection: sqlite3.Connection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = connection

    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Login")
