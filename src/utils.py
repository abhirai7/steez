from __future__ import annotations

import base64
import locale
import pathlib
import random
import string
from typing import TYPE_CHECKING

import qrcode
from dotenv import load_dotenv
from qrcode.constants import ERROR_CORRECT_H

if TYPE_CHECKING:
    from PIL import Image

load_dotenv()

REGION = "en_IN"


class _CaseInsensitiveDict(dict):
    def __setitem__(self, key, value) -> None:
        super().__setitem__(key.casefold(), value)

    def __getitem__(self, key) -> str:
        return super().__getitem__(key.casefold())

    def __delitem__(self, key) -> None:
        super().__delitem__(key.casefold())

    def __contains__(self, key) -> bool:
        return super().__contains__(key.casefold())

    def get(self, key, default=None) -> str:
        return super().get(key.casefold(), default)

    def pop(self, key, default=None) -> str:
        return super().pop(key.casefold(), default)


special_letters = {
    "a": ["á", "à", "â", "ä", "ã", "å", "ā"],
    "b": ["b"],
    "c": ["ç", "ć", "č"],
    "d": ["ď", "ð"],
    "e": ["é", "è", "ê", "ë", "ē", "ė", "ę"],
    "f": ["f"],
    "g": ["ğ"],
    "h": ["ħ"],
    "i": ["í", "ì", "î", "ï", "ī"],
    "j": ["j"],
    "k": ["ķ"],
    "l": ["ł"],
    "m": ["m"],
    "n": ["ñ", "ń"],
    "o": ["ó", "ò", "ô", "ö", "õ", "ō"],
    "p": ["p"],
    "q": ["q"],
    "r": ["ř"],
    "s": ["ś", "š"],
    "t": ["ť"],
    "u": ["ú", "ù", "û", "ü", "ū"],
    "v": ["v"],
    "w": ["w"],
    "x": ["x"],
    "y": ["ý", "ÿ"],
    "z": ["ž", "ź", "ż"],
}


def format_to_special(text: str, /) -> str:
    result = []
    text = text.lower()
    for char in text:
        if char in special_letters:
            result.append(random.choice(special_letters[char]))
        else:
            result.append(char)
    return "".join(result)


def get_product_pictures(product_id: int | str) -> list[str]:
    this_path = pathlib.Path(__file__).parent
    path = this_path / "server" / "static" / "product_pictures" / str(product_id)

    if not path.exists():
        return []

    files = []
    for file in path.iterdir():
        path_from_static = file.relative_to(this_path / "server")
        files.append(f"/{str(path_from_static)}")

    return files


size_chart = {
    "XX-SMALL": {"CHEST": "37''", "LENGTH": "26.5''", "CODE": "1"},
    "X-SMALL": {"CHEST": "39''", "LENGTH": "27''", "CODE": "10"},
    "SMALL": {"CHEST": "41''", "LENGTH": "27.5''", "CODE": "100"},
    "MEDIUM": {"CHEST": "43''", "LENGTH": "28''", "CODE": "1000"},
    "LARGE": {"CHEST": "45''", "LENGTH": "29''", "CODE": "10000"},
    "X-LARGE": {"CHEST": "47''", "LENGTH": "30''", "CODE": "100000"},
    "XX-LARGE": {"CHEST": "51''", "LENGTH": "31''", "CODE": "1000000"},
    "XXX-LARGE": {"CHEST": "53''", "LENGTH": "32''", "CODE": "10000000"},
}

size_names = {
    "1": "XX-SMALL",
    "10": "X-SMALL",
    "100": "SMALL",
    "1000": "MEDIUM",
    "10000": "LARGE",
    "100000": "X-LARGE",
    "1000000": "XX-LARGE",
    "10000000": "XXX-LARGE",
}


def format_number(number: int, /) -> str:
    return locale.format_string("%d", number, grouping=True)


def generate_gift_card_code(k: int = 16) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=k))


def binary_adder(a: str, b: str) -> str:
    return bin(int(a, 2) + int(b, 2))[2:]


class FAQEntity:
    def __init__(self, question: str, answer: str, /) -> None:
        self.question = question
        self.answer = answer


class FAQ:
    def __init__(self, /) -> None:
        self.__faqs: list[FAQEntity] = []

    def add(self, question: str, answer: str, /) -> None:
        self.__faqs.append(FAQEntity(question, answer))

    def get(self) -> list[FAQEntity]:
        return self.__faqs

    def __iter__(self):
        return iter(self.__faqs)

    def __len__(self):
        return len(self.__faqs)


with open("src/server/static/faq.json") as f:
    import json

    faq_data = json.load(f)

faq = FAQ()
for faq_entity in faq_data["faq"]:
    faq.add(faq_entity["question"], faq_entity["answer"])

FAQ_DATA = faq


def newsletter_email_add_to_db(conn: Connection, /, *, email: str) -> None:
    cur = conn.cursor()
    query = "INSERT OR IGNORE INTO NEWSLETTERS (EMAIL) VALUES (?)"

    cur.execute(query, (email,))
    conn.commit()


def backup_sqlite_database(
    conn: Connection, /, *, path: str = "database-bak.sqlite"
) -> None:
    backup_path_connection = Connection(path)
    with backup_path_connection:
        conn.backup(backup_path_connection)
    backup_path_connection.close()


class OrderQR:
    BASE62_CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase
    BASE = len(BASE62_CHARS)

    def __init__(self, /, *, order_id: int) -> None:
        self.__order_id = order_id

    def generate_qr_code(self, /) -> Image.Image:
        text = "QR_" + self.num_to_text(self.__order_id)
        text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        qr = qrcode.QRCode(
            version=40,
            error_correction=ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        return img

    def num_to_text(self, num: int):
        if num == 0:
            return OrderQR.BASE62_CHARS[0]

        result = []
        while num > 0:
            remainder = num % OrderQR.BASE
            result.append(OrderQR.BASE62_CHARS[remainder])
            num //= OrderQR.BASE

        return "".join(reversed(result))

    def text_to_num(self, text: str):
        num = 0
        for char in text:
            num = num * OrderQR.BASE + OrderQR.BASE62_CHARS.index(char)

        return num
