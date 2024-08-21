from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField
from wtforms.validators import DataRequired


class ProductAddForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    price = StringField("Price", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    images = MultipleFileField("Image", validators=[DataRequired()])
    stock = StringField("Stock", validators=[DataRequired()])
    submit = SubmitField("Add Product")


class ProductEditForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    price = StringField("Price", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    images = MultipleFileField("Image", validators=[DataRequired()])
    stock = StringField("Stock", validators=[DataRequired()])
    submit = SubmitField("Edit Product")
