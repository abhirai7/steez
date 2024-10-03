from __future__ import annotations

import json

from flask import render_template, request

from src.order import Order
from src.server import admin_login_required, app, conn, razorpay_client


@app.route("/admin/manage/razorpay-orders", methods=["GET"])
@admin_login_required
def admin_manage_razorpay_order():
    page = max(int(request.args.get("page", 1)), 1)
    limit = int(request.args.get("limit", 15))
    skip = (page - 1) * limit

    response = razorpay_client.order.all({"count": limit, "skip": skip})

    total_order_amount = sum(item["amount"] for item in response["items"])
    total_paid = sum(item["amount_paid"] for item in response["items"] if item["amount_paid"])
    total_due = sum(item["amount_due"] for item in response["items"])

    return render_template(
        "admin/admin_manage_order.html",
        total_order_amount=total_order_amount,
        total_paid=total_paid,
        total_due=total_due,
        response=response,
        skip=skip,
        page=page,
        limit=limit,
        json=json,
    )


@app.route("/admin/manage/orders", methods=["GET"])
@admin_login_required
def admin_manage_order():
    page = max(int(request.args.get("page", 1)), 1)
    limit = int(request.args.get("limit", 15))
    skip = (page - 1) * limit

    orders = Order.all(conn, limit=limit, offset=skip)

    return render_template(
        "admin/admin_manage_partial_order.html",
        orders=orders,
        page=page,
        skip=skip,
        limit=limit,
    )


@app.route("/admin/payouts", methods=["GET"])
@admin_login_required
def admin_payments():
    page = max(int(request.args.get("page", 1)), 1)
    limit = int(request.args.get("limit", 15))
    skip = (page - 1) * limit

    payments = razorpay_client.payment.all({"count": limit, "skip": skip})

    return render_template(
        "admin/admin_payments.html",
        payments=payments,
        page=page,
        skip=skip,
        limit=limit,
    )
