import locale

import arrow

from src.server import app

try:
    locale.setlocale(locale.LC_ALL, "en_IN")
except locale.Error:
    pass


@app.template_filter("datetimeformat")
def datetimeformat(value):
    dt = arrow.get(value)
    return f"{dt.format('YYYY-MM-DD HH:mm:ss')} ({dt.humanize()})"


@app.template_filter("format_currency")
def format_currency(value):
    try:
        return locale.currency((value or 0) / 100, grouping=True)
    except ValueError:
        return value
