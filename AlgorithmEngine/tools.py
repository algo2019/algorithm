import re
import datetime

_use_pylib_tag = False


def format_to_datetime(dt, time=True, date=True, ms=True):
    ds = re.match(r'\s*(?:(\d{4})[\:\-\/]?(\d{2})[\:\-\/]?(\d{2}))?\s?T?(?:(\d{2}):?(\d{2}):?(\d{2})\.?(\d+)?)?\s*', str(dt))
    if ds is not None:
        if not time:
            return datetime.date(*map(int, ds.groups(default=0)[:3]))
        if not date:
            if not ms:
                return datetime.time(*map(int, ds.groups(default=0)[3:6]))
            return datetime.time(*map(int, ds.groups(default=0)[3:]))
        if not ms:
            return datetime.datetime(*map(int, ds.groups(default=0)[:6]))
        return datetime.datetime(*map(int, ds.groups(default=0)))
    else:
        raise Exception('format_to_datetime: can not format {} to datetime'.format(dt))


def use_pylib():
    global _use_pylib_tag
    if not _use_pylib_tag:
        import sys
        import os
        sys.path.append(os.path.abspath(os.path.join(__file__, '..', 'pylib')))
        _use_pylib_tag = True

