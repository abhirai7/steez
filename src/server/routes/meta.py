from __future__ import annotations

from flask import make_response, render_template, request

from src.server import app, sitemapper


@app.route("/sitemap.xml")
def sitemap():
    return sitemapper.generate(), 200, {"Content-Type": "application/xml"}


@app.route("/set-cookie")
def set_cookie():
    response = make_response("Cookie has been set")

    response.set_cookie(
        "user_fingerprint_v2",
        "value",
        path="/",
        secure=True,
        samesite="None",
        httponly=False,
    )

    response.headers.add(
        "Set-Cookie",
        "user_fingerprint_v2=value; Path=/; Secure; SameSite=None; Partitioned",
    )

    return response


@app.before_request
def before_request():
    if "user_fingerprint_v2" not in request.cookies:
        set_cookie()
    return None


@app.route("/payment-success")
def payment_success():
    return render_template("payment_status.html", status="ok")


@app.route("/payment-failure")
def payment_failure():
    return render_template("payment_status.html", status="error")
