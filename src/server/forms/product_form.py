from flask_wtf import FlaskForm
from wtforms import (
    FloatField,
    IntegerField,
    MultipleFileField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, NumberRange

from src.utils import size_chart


class ProductAddForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    images = MultipleFileField("Image", validators=[DataRequired()])
    stock = IntegerField("Stock", validators=[DataRequired()])
    sizes = SelectMultipleField(
        "Size",
        validators=[DataRequired()],
        choices=[(data["CODE"], size) for size, data in size_chart.items()],
    )
    submit = SubmitField("Add Product")


class GiftCardForm(FlaskForm):
    amount = IntegerField(
        "Amount", validators=[DataRequired(), NumberRange(min=100, max=2000)]
    )
    submit = SubmitField("Buy Gift Card")
