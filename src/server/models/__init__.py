from __future__ import annotations

from .carousel import Carousel  # noqa
from .cart import Cart  # noqa
from .category import Category  # noqa
from .favourite import Favourite  # noqa
from .gift_card import GiftCard  # noqa
from .newsletter import Newsletter  # noqa
from .order import Order  # noqa
from .product import Product  # noqa
from .return_request import ReturnRequest  # noqa
from .review import Review  # noqa
from .role import Role
from .ticket import Ticket  # noqa
from .user import User  # noqa

__all__ = [
    "Carousel",
    "Cart",
    "Category",
    "Favourite",
    "GiftCard",
    "Newsletter",
    "Order",
    "Product",
    "ReturnRequest",
    "Review",
    "Ticket",
    "User",
    "Role",
]

__models__: list = [
    User,
    Product,
    Order,
    Carousel,
    Cart,
    Category,
    Favourite,
    GiftCard,
    Newsletter,
    ReturnRequest,
    Review,
    Ticket,
    Role,
]
