from flask_wtf import FlaskForm
from wtforms import (
    FloatField,
    IntegerField,
    MultipleFileField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired


class ProductAddForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    images = MultipleFileField("Image", validators=[DataRequired()])
    stock = IntegerField("Stock", validators=[DataRequired()])
    submit = SubmitField("Add Product")


class ProductEditForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    images = MultipleFileField("Image", validators=[DataRequired()])
    stock = IntegerField("Stock", validators=[DataRequired()])
    submit = SubmitField("Edit Product")
