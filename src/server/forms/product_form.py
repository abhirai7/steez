from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from flask_wtf import FlaskForm
from wtforms import (
    EmailField,
    FileField,
    FloatField,
    IntegerField,
    MultipleFileField,
    SearchField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, NumberRange

from src.product import Category
from src.utils import size_chart

if TYPE_CHECKING:
    from src.product import Product

# fmt: off

class ProductAddForm(FlaskForm):
    name          = StringField("Product Name", validators=[DataRequired()])
    display_price = FloatField("Price")
    price         = FloatField("Actual Price", validators=[DataRequired()])
    description   = TextAreaField("Description", validators=[DataRequired()])
    images        = MultipleFileField("Image", validators=[DataRequired()])
    stock         = IntegerField("Stock", validators=[DataRequired()])
    sizes         = SelectMultipleField("Size", validators=[DataRequired()], choices=[(data["CODE"], size) for size, data in size_chart.items()])
    category      = SelectField("Category", validators=[DataRequired()], choices=[])
    keywords      = StringField("Keywords")
    submit        = SubmitField("Add Product")

    def __init__(self, connection: sqlite3.Connection, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.conn = connection
        self.category.choices = [(int(category.id), category.name) for category in Category.all(connection)]


class ProductUpdateForm(FlaskForm):
    name          = StringField("Product Name")
    display_price = FloatField("Price")
    price         = FloatField("Actual Price")
    description   = TextAreaField("Description")
    stock         = IntegerField("Stock")
    sizes         = SelectField("Size", choices=[(data["CODE"], size) for size, data in size_chart.items()])
    category      = SelectField("Category", choices=[], validators=[DataRequired()])
    keywords      = StringField("Keywords")

    submit        = SubmitField("Update Product")

    def validate_on_submit(self, extra_validators=None):
        return True

    def __init__(self, connection: sqlite3.Connection, *args, product: Product, **kwargs):
        super().__init__(*args, **kwargs)

        self.conn = connection
        self.category.choices = [(int(category.id), category.name) for category in Category.all(connection)]
        self.product = product

        self.category.data = product.category.id
        self.category.default = product.category.id


class CategoryAddForm(FlaskForm):
    name        = StringField("Category Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit      = SubmitField("Add Category")


class CarouselForm(FlaskForm):
    heading     = StringField("Heading", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    image       = FileField("Image", validators=[DataRequired()])

    submit      = SubmitField("Update Carousel")


class GiftCardForm(FlaskForm):
    amount = IntegerField("Amount", validators=[DataRequired(), NumberRange(min=50, max=2000)], default=100)
    submit = SubmitField("Buy Gift Card")


class SearchForm(FlaskForm):
    query  = SearchField("Search", validators=[DataRequired()])
    submit = SubmitField("Search")

class SubscribeNewsLetterForm(FlaskForm):
    email       = EmailField("Email")
    subscribe   = SubmitField("Subscribe")

class PaymentMethod(FlaskForm):
    gift_card = StringField("Gift Card")
    method = SelectField("Select Payment Method", choices=[("cash", "Cash on Delivery"), ("razorpay", "Pay via Razorpay")], default="razorpay", validators=[DataRequired()])
    final_checkout = SubmitField("Looks Good! Proceed to Checkout")

# fmt: on
