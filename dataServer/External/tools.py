import re
import datetime


EXCHANGE_ID = {
    'SHF': {'IM', 'AL', 'AU', 'NI', 'PB', 'CU', 'SN', 'ZN', 'AG', 'BU', 'RB', 'FU', 'HC', 'WR', 'RU'},
    'DCE': {'V', 'B', 'M', 'A', 'Y', 'JD', 'JM', 'J', 'BB', 'PP', 'L', 'I', 'FB', 'C', 'CS', 'P'},
    'CZC': {'SR', 'CF', 'ZC', 'FG', 'TA', 'MA', 'WH', 'PM', 'R', 'LR', 'JR', 'RS', 'OI', 'RM', 'SF', 'SM', 'RI'},
    'CFE': {'IF', 'IH', 'IC', 'TF', 'T', 'TT', 'AF', 'EF'}
}


def format_to_datetime(dt, time=True, date=True, ms=True):
    ds = re.match(r'\s*(?:(\d{4})[\:\-\/]?(\d{2})[\:\-\/]?(\d{2}))?\s?(?:(\d{2}):?(\d{2}):?(\d{2})\.?(\d+)?)?\s*', str(dt))
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


def get_dict_data(data):
    if type(data) is dict:
        data = data['data']
    return {item[0]: item[1] for item in (i.split('#') for i in data.split('|'))}


def get_exchange_id(instrument_or_symbol):
    import re
    symbol = re.sub(r'\d', '', instrument_or_symbol).upper()
    for key in EXCHANGE_ID:
        if symbol in EXCHANGE_ID[key]:
            return key
    return ''
