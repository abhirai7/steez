import contextlib
import locale

import arrow

from src.server import app

with contextlib.suppress(locale.Error):
    locale.setlocale(locale.LC_ALL, "en_IN")


@app.template_filter("datetimeformat")
def datetimeformat(value):
    dt = arrow.get(value)
    return f"{dt.format('YYYY-MM-DD HH:mm:ss')} ({dt.humanize()})"

@app.template_filter("datetimeformat_short")
def datetimeformat_short(value):
    dt = arrow.get(value)
    return dt.humanize()


@app.template_filter("format_currency")
def format_currency(value):
    try:
        cur = locale.currency((value or 0) / 100, grouping=True)
        RUPEE = "₹"
        return cur.replace(RUPEE, "INR. ")
    except ValueError:
        return f"INR. {(value or 0) / 100}"

@app.template_filter("format_currency_direct")
def format_currency_direct(value):
    try:
        cur = locale.currency((value or 0), grouping=True)
        RUPEE = "₹"
        return cur.replace(RUPEE, "INR. ")
    except ValueError:
        return f"{(value or 0)}"