from __future__ import annotations

import sqlite3

from flask_wtf import FlaskForm
from wtforms import (
    FileField,
    FloatField,
    IntegerField,
    MultipleFileField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, NumberRange

from src.product import Category
from src.utils import size_chart

# fmt: off

class ProductAddForm(FlaskForm):
    name          = StringField("Product Name", validators=[DataRequired()])
    display_price = FloatField("Display Price")
    price         = FloatField("Price", validators=[DataRequired()])
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
    amount = IntegerField("Amount", validators=[DataRequired(), NumberRange(min=50, max=2000)])
    submit = SubmitField("Buy Gift Card")

# fmt: off
