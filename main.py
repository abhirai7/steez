from src.server import app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
"""
import razorpay
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.type_hints import Client as RazorpayClient
else:
    RazorpayClient = razorpay.Client
from dotenv import load_dotenv

load_dotenv()

RAZORPAY_KEY = os.getenv("RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")

assert RAZORPAY_KEY is not None and RAZORPAY_SECRET is not None

razorpay_client: RazorpayClient = RazorpayClient(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))

razorpay_client.set_app_details({"title": "Flask E-commerce", "version": "1.0"})


def create_order(amount: int, currency: str = "INR") -> dict:
    order = razorpay_client.order.create({"amount": amount, "currency": currency})
    return order


def verify_payment(payment_id: str, amount: int) -> bool:
    payment = razorpay_client.payment.fetch(payment_id)
    return payment["amount"] == amount


def capture_payment(payment_id: str, amount: int) -> bool:
    payment = razorpay_client.payment.capture(payment_id, amount)
    return payment["status"] == "captured"


def refund_payment(payment_id: str, amount: int) -> bool:
    refund = razorpay_client.payment.refund(payment_id, amount)
    return refund["status"] == "processed"


if __name__ == "__main__":

    client = razorpay_client
    orders = client.order.all()
    print(orders)
"""
