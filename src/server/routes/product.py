from flask import render_template

from src.product import Product
from src.server import app, conn
from src.utils import format_to_special, get_product_pictures


@app.route("/product/<int:product_id>")
def product(product_id: int):
    product = Product.from_id(conn, product_id)
    pictures = get_product_pictures(product_id)

    return render_template(
        "product.html",
        product=product,
        pictures=pictures,
        format_to_special=format_to_special,
    )
