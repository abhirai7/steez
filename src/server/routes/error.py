from flask import render_template

from src.server import app


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error/404.html"), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("error/403.html"), 403


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error/500.html"), 500


@app.errorhandler(502)
def bad_gateway(e):
    return render_template("error/502.html"), 502


@app.errorhandler(503)
def service_unavailable(e):
    return render_template("error/503.html"), 503


@app.errorhandler(504)
def gateway_timeout(e):
    return render_template("error/504.html"), 504


@app.errorhandler(505)
def http_version_not_supported(e):
    return render_template("error/505.html"), 505
