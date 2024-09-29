import random
import sqlite3
import string
import os
from PIL import Image
import first  # noqa

from src.product import Category, Product
from src.carousel import Carousel
from src.utils import size_names, sqlite_row_factory
first

cmd = "rm database*.sqlite*"
os.system(cmd)


conn = sqlite3.connect("database.sqlite")
with open("schema.sql") as f:
    conn.executescript(f.read())

conn.row_factory = sqlite_row_factory
conn.commit()

UPLOAD_FOLDER = "src/server/static/product_pictures"
PRICES = [1800, 1900, 1799, 1500, 2500, 3000]
DISPLAY_PRICE = [2000, 2100, 1999, 1600, 2700, 3600]
KEYWORDS = ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"]


def generate_unique_identifier():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=16))


product_image_path = [r"front-image.png", r"back-image.png"]
carosel_image_path = r"placeholder-2000x800.png"

for i in range(1, 4):
    cat = Category.create(conn, name=f"Category {i}", description=f"Category {i} Description")

    imgs = [Image.open(path) for path in product_image_path]
    for k in range(10):
        sub_folder = generate_unique_identifier()

        for j, img in enumerate(imgs):
            if not os.path.exists(f"{UPLOAD_FOLDER}/{sub_folder}"):
                os.makedirs(f"{UPLOAD_FOLDER}/{sub_folder}")

            img.save(f"{UPLOAD_FOLDER}/{sub_folder}/{j}-{generate_unique_identifier()}.png")

        for size in size_names:
            Product.create(
                conn,
                unique_id=sub_folder,
                name=f"Product {k}",
                price=PRICES[k % len(PRICES)],
                display_price=DISPLAY_PRICE[k % len(DISPLAY_PRICE)],
                stock=random.randint(1, 100),
                description=f"Product {k} Description",
                category=cat.id,
                keywords=";".join(random.choices(KEYWORDS, k=3)),
                size=size,
            )

caro_image = Image.open(carosel_image_path)
sub_folder = generate_unique_identifier()
if not os.path.exists(f"{UPLOAD_FOLDER}/{sub_folder}"):
    os.makedirs(f"{UPLOAD_FOLDER}/{sub_folder}")

caro_image.save(f"{UPLOAD_FOLDER}/{sub_folder}/{generate_unique_identifier()}.png")

for i in range(1, 4):
    Carousel.create(conn, image=sub_folder, heading="Carousel Heading", description="Carousel Description")

conn.commit()
conn.close()