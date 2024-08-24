import sqlite3

from flask_wtf import FlaskForm
from wtforms import EmailField, IntegerField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from src.user import User


class LoginForm(FlaskForm):
    def __init__(self, connection: sqlite3.Connection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = connection
        self.user: User | None = None

    email = EmailField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])

    submit = SubmitField("Login")

    def validate_on_submit(self):
        if not super().validate_on_submit():
            return False

        assert self.email.data and self.password.data

        try:
            user = User.from_email(
                self.conn, email=self.email.data, password=self.password.data
            )
        except ValueError:
            return False
        else:
            self.user = user

        return True


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
    address_line2 = StringField("Address Line 2")

    city = StringField("", validators=[DataRequired()])
    state = StringField("", validators=[DataRequired()])
    pincode = IntegerField("", validators=[DataRequired()])
    phone = IntegerField("", validators=[DataRequired()])

    submit = SubmitField("Register")

    def validate_email(self, email: EmailField):
        assert email.data

        str_email = email.data.lower()

        user = User.exists(self.conn, email=str_email)
        if user:
            raise ValidationError("Email already registered")

        return True

    def validate_phone(self, phone: IntegerField):
        assert phone.data

        phone_str = str(phone.data)
        if len(phone_str) != 10:
            raise ValidationError("Phone number must be 10 digits long")

        return True

    def validate_pincode(self, pincode: IntegerField):
        assert pincode.data

        pincode_str = str(pincode.data)
        if len(pincode_str) != 6:
            raise ValidationError("Pincode must be 6 digits long")

        return True


class AdminForm(FlaskForm):
    def __init__(self, connection: sqlite3.Connection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = connection

    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Login")


from .cart import *  # noqa
from .product_form import *  # noqa
