from datetime import datetime
from datetime import timedelta
from datetime import timezone


def next_hhmm(hhmm, now):
    """
    :param hhmm: time of the day as a string "HH:MM"
    :param now: datetime when the function is called
    :return: datetime of the next HH:MM, same TZ
    """
    h, m = (int(x) for x in hhmm.split(":"))
    base_date = now.date()
    if now.hour >= h:
        base_date = base_date + timedelta(days=1)
    target = datetime(
        year=base_date.year,
        month=base_date.month,
        day=base_date.day,
        hour=h,
        minute=m,
        tzinfo=now.tzinfo)
    return target


def next_quiz_time(last_quiz_time, now=None):
    """
    :param last_quiz_time: the previous time quiz was scheduled
    :param now: timestamp when the function is called
    :return: same time + 1 day (i.e. tomorrow)
    """
    if now is None:
        now = datetime.now(tz=timezone.utc)
    tomorrow_date = now.date() + timedelta(days=1)
    return last_quiz_time.replace(year=tomorrow_date.year,
                                  month=tomorrow_date.month,
                                  day=tomorrow_date.day)
