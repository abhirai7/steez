from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField, TextAreaField
from wtforms.validators import NumberRange

from src.utils import size_chart, size_names


class AddToCartForm(FlaskForm):
    size = SelectField(
        "Size",
        choices=[(size_chart[size]["CODE"], size) for size in size_chart],
    )

    quantity = IntegerField("Quantity", validators=[NumberRange(min=1)])
    submit = SubmitField("Add to Cart")

    def __init__(self, available_sizes: list[str] | None = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if available_sizes:
            self.size.choices = [(size, size_names[size]) for size in available_sizes]

class AddReviewForm(FlaskForm):
    review = TextAreaField("Review")
    submit = SubmitField("Add Review")
