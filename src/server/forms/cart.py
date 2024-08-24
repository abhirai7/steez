from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField, TextAreaField

from src.utils import size_chart


class AddToCartForm(FlaskForm):
    quantity = IntegerField("Quantity")
    size = SelectField(
        "Size",
        choices=[(size, size) for size, data in size_chart.items()],
    )

    submit = SubmitField("Add to Cart")

    def validate_on_submit(self):
        if not super().validate_on_submit():
            return False

        return True


class AddReviewForm(FlaskForm):
    review = TextAreaField("Review")
    submit = SubmitField("Add Review")

    def validate_on_submit(self):
        if not super().validate_on_submit():
            return False

        return True
