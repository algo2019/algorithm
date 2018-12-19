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


def get_symbol(instrument):
    return re.sub(r'\d', '', instrument).upper()


def get_exchange_id(symbol_or_instrument):
    symbol = get_symbol(symbol_or_instrument)
    for id in EXCHANGE_ID:
        if symbol in EXCHANGE_ID[id]:
            return id
    return None


EXCHANGE_ID = {
    'SHFX': {'IM', 'AL', 'AU', 'NI', 'PB', 'CU', 'SN', 'ZN', 'AG', 'BU', 'RB', 'FU', 'HC', 'WR', 'RU'},
    'DLFX': {'V', 'B', 'M', 'A', 'Y', 'JD', 'JM', 'J', 'BB', 'PP', 'L', 'I', 'FB', 'C', 'CS', 'P'},
    'ZZFX': {'SR', 'CF', 'ZC', 'FG', 'TA', 'MA', 'WH', 'PM', 'R', 'LR', 'JR', 'RS', 'OI', 'RM', 'SF', 'SM', 'RI'},
    'CFFEX': {'IF', 'IH', 'IC', 'TF', 'T', 'TT', 'AF', 'EF'}
}