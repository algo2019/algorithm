import re
import datetime


def format_to_datetime(dt, time=True, date=True, ms=True):
    ds = re.match(r'(\d{4})[\:\-\/]?(\d{2})[\:\-\/]?(\d{2})\s?(?:(\d{2}):?(\d{2}):?(\d{2})\.?(\d+)?)?', str(dt))
    if ds is not None:
        if not time:
            return datetime.date(*map(int, ds.groups(default=0)[:3]))
        if not date:
            if not ms:
                return datetime.time(*map(int, ds.groups(default=0)[3:6]))
            return datetime.time(*map(int, ds.groups(default=0)[3:]))
        return datetime.datetime(*map(int, ds.groups(default=0)))
    else:
        raise Exception('format_to_datetime: can not format {} to datetime'.format(dt))
