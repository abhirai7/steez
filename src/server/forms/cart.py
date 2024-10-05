from __future__ import annotations

from typing import TYPE_CHECKING

from flask_wtf import FlaskForm
from wtforms import IntegerField, RadioField, SelectField, SubmitField, TextAreaField
from wtforms.validators import NumberRange, ValidationError

from src.utils import size_chart, size_names

if TYPE_CHECKING:
    from src.product import Product


class AddToCartForm(FlaskForm):
    size = SelectField(
        "Select Size",
        choices=[(size_chart[size]["CODE"], size) for size in size_chart],
        default="select",
    )

    quantity = IntegerField("Quantity", validators=[NumberRange(min=1)], default=1)
    submit = SubmitField("Add to Cart")

    def __init__(self, product: Product | None = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if product and product.available_sizes:
            self.size.choices = [("select", "Select Size")] + [
                (size, size_names[size]) for size in product.available_sizes
            ]  # type: ignore
            self.size.default = "select"

        if product and product.stock > 1:
            self.quantity.validators = [NumberRange(min=1, max=product.stock - 1)] if product else [NumberRange(min=1)]

    def validate_size(self, size: SelectField) -> bool:
        if size.data == "select":
            raise ValidationError("Please select a size")
        return True


class AddReviewForm(FlaskForm):
    review = TextAreaField("Review")
    stars = RadioField(
        "",
        choices=[(str(i), str(i)) for i in range(1, 6)],
        default="5",
    )
    submit = SubmitField("Add Review")
