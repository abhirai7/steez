from __future__ import annotations

from flask_security.forms import RegisterForm as _RegisterForm
from wtforms import Field, IntegerField, StringField, SubmitField, TelField
from wtforms.validators import DataRequired, ValidationError


class RegisterForm(_RegisterForm):
    name = StringField("Person Details", validators=[DataRequired()], render_kw={"autocomplete": "off"})

    address = StringField(
        "Address Details",
        validators=[DataRequired()],
        render_kw={"autocomplete": "off"},
    )

    city = StringField("", validators=[DataRequired()], render_kw={"autocomplete": "off"})
    state = StringField("", validators=[DataRequired()], render_kw={"autocomplete": "off"})
    pincode = IntegerField("", validators=[DataRequired()], render_kw={"autocomplete": "off"})
    phone = TelField("", validators=[DataRequired()], render_kw={"autocomplete": "off"})

    register = SubmitField("Register")

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
