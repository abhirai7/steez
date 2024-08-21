import sqlite3

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from src.user import User


class IntegerNumber:
    def __init__(self, message: str = "Not a valid number"):
        self.message = message

    def __call__(self, form, field):
        try:
            int(field.data)
        except ValueError:
            raise ValidationError(self.message)


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
    pincode = StringField("", validators=[DataRequired(), Length(min=6), Length(max=6)])
    phone = StringField("", validators=[DataRequired(), Length(min=10), Length(max=10), IntegerNumber()])

    submit = SubmitField("Register")

    def validate_email(self, email: EmailField):
        assert email.data

        str_email = email.data.lower()

        user = User.exists(self.conn, email=str_email)
        if user:
            raise ValidationError("Email already registered")

        return True
