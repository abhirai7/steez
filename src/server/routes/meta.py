from __future__ import annotations

from flask import make_response, request

from src.server import app, logger, sitemapper


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
    # IP address, HTTP method, and path, status code
    logger.debug("%s [%s] %s", request.remote_addr, request.method, request.path)
    if "user_fingerprint_v2" not in request.cookies:
        set_cookie()
    return None
