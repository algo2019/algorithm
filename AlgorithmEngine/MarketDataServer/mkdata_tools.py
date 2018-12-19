import re

TRADEUNIT = {
    u'A': 10,
    u'AG': 15,
    u'AL': 5,
    u'AU': 1000,
    u'B': 10,
    u'BB': 500,
    u'BU': 10,
    u'C': 10,
    u'CF': 5,
    u'CS': 10,
    u'CU': 5,
    u'ER': 10,
    u'FB': 500,
    u'FG': 20,
    u'FU': 50,
    u'GN': 10,
    u'HC': 10,
    u'I': 100,
    u'J': 100,
    u'JD': 5,
    u'JM': 60,
    u'JR': 20,
    u'L': 5,
    u'LR': 20,
    u'M': 10,
    u'MA': 10,
    u'ME': 50,
    u'NI': 1,
    u'OI': 10,
    u'P': 10,
    u'PB': 5,
    u'PM': 50,
    u'PP': 5,
    u'RB': 10,
    u'RI': 20,
    u'RM': 10,
    u'RO': 5,
    u'RS': 10,
    u'RU': 10,
    u'S': 10,
    u'SF': 5,
    u'SM': 5,
    u'SN': 1,
    u'SR': 10,
    u'TA': 5,
    u'TC': 200,
    u'V': 5,
    u'WH': 20,
    u'WR': 10,
    u'WS': 10,
    u'WT': 10,
    u'Y': 10,
    u'ZC': 100,
    u'ZN': 5
}

EXCHANGE_ID = {
    'SHFX': {'IM', 'AL', 'AU', 'NI', 'PB', 'CU', 'SN', 'ZN', 'AG', 'BU', 'RB', 'FU', 'HC', 'WR', 'RU'},
    'DLFX': {'V', 'B', 'M', 'A', 'Y', 'JD', 'JM', 'J', 'BB', 'PP', 'L', 'I', 'FB', 'C', 'CS', 'P'},
    'ZZFX': {'SR', 'CF', 'ZC', 'FG', 'TA', 'MA', 'WH', 'PM', 'R', 'LR', 'JR', 'RS', 'OI', 'RM', 'SF', 'SM', 'RI'},
    'CFFEX': {'IF', 'IH', 'IC', 'TF', 'T', 'TT', 'AF', 'EF'}
}


def get_exchange_id(instrument_or_symbol):
    import re
    symbol = re.sub(r'\d', '', instrument_or_symbol).upper()
    for key in EXCHANGE_ID:
        if symbol in EXCHANGE_ID[key]:
            return key
    return ''


def get_trade_unit(instrument):
    return TRADEUNIT.get(re.sub(r'^([a-zA-Z]+)\d+$', r'\1', instrument).upper(), 1)


def get_dict_data(data):
    if type(data) is dict:
        data = data['data']
    return {item[0]: item[1] for item in (i.split('#') for i in data.split('|'))}
