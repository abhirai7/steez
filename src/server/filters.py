import locale

import arrow

from src.server import app

locale.setlocale(locale.LC_ALL, "en_IN")


@app.template_filter("datetimeformat")
def datetimeformat(value):
    dt = arrow.get(value)
    return f"{dt.format('YYYY-MM-DD HH:mm:ss')} ({dt.humanize()})"


@app.template_filter("format_currency")
def format_currency(value):
    return locale.currency((value or 0) / 100, grouping=True)
