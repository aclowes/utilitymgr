import datetime

import pytz


def today_pacific():
    return datetime.datetime.now(tz=pytz.utc).astimezone(pytz.timezone('US/Pacific')).date()


def week_start_end():
    today = today_pacific()
    return (
        today - datetime.timedelta(days=6),
        today + datetime.timedelta(days=1)
    )
