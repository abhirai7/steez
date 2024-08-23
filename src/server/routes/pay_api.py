from typing import TYPE_CHECKING

from flask_login import current_user, login_required

from src.product import Product
from src.server import app, conn, razorpay_client
from src.user import User

if TYPE_CHECKING:
    assert isinstance(current_user, User)


@app.route("/user/<int:user_id>/create_order", methods=["POST"])
@login_required
def create_order(user_id: int):
    assert current_user.id == user_id

    return current_user.full_checkout(razorpay_client)


@app.route("/user/<int:user_id>/orders", methods=["GET"])
@login_required
def get_orders(user_id: int):
    assert current_user.id == user_id

    return current_user.partial_checkout()


@app.route("/user/<int:user_id>/cart", methods=["GET"])
@login_required
def get_order(user_id: int, order_id: int):
    assert current_user.id == user_id

    return current_user.cart.get_products(json=True)


@app.route("/user/<int:user_id>/cart", methods=["POST"])
@login_required
def add_to_cart(user_id: int, product_id: int):
    assert current_user.id == user_id

    current_user.cart.add_product(product=Product.from_id(conn, product_id=product_id))

    return current_user.cart.get_products(json=True)


@app.route("/user/<int:user_id>/cart", methods=["DELETE"])
@login_required
def remove_from_cart(user_id: int, product_id: int):
    assert current_user.id == user_id

    current_user.cart.remove_product(
        product=Product.from_id(conn, product_id=product_id)
    )

    return current_user.cart.get_products(json=True)
