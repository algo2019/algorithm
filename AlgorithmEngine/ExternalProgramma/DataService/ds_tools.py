import json as _json
import datetime
import dateutil.parser
import decimal
import sys


__all__ = ['json', 'instead_json']

CONVERTERS = {
    'datetime': {
        'type': datetime.datetime,
        'parser': dateutil.parser.parse,
        'format': lambda x: x.isoformat(),
    },
    'date': {
        'type': datetime.date,
        'parser': dateutil.parser.parse,
        'format': lambda x: x.isoformat(),
    },
    'decimal': {
        'type': decimal.Decimal,
        'parser': decimal.Decimal,
        'format': str,
    },
}


class MyJSONEncoder(_json.JSONEncoder):
    def default(self, obj):
        for tn in CONVERTERS:
            config = CONVERTERS[tn]
            if isinstance(obj, config['type']):
                return {"val": config['format'](obj), "_spec_type": tn}
        return super(MyJSONEncoder, self).default(obj)


def object_hook(obj):
    _spec_type = obj.get('_spec_type')
    if not _spec_type:
        return obj

    if _spec_type in CONVERTERS:
        return CONVERTERS[_spec_type]['parser'](obj['val'])
    else:
        raise Exception('Unknown {}'.format(_spec_type))


class json(object):
    @staticmethod
    def dumps(data, **kwargs):
        kwargs['cls'] = kwargs.get('cls') or MyJSONEncoder
        return _json.dumps(data, **kwargs)

    @staticmethod
    def loads(thing, **kwargs):
        kwargs['object_hook'] = kwargs.get('object_hook') or object_hook
        return _json.loads(thing, **kwargs)

    @classmethod
    def __getattribute__(cls, item):
        if item in {'dumps', 'loads'}:
            return super(json, cls).__getattribute__(item)
        else:
            return getattr(_json, item)


def instead_json():
    sys.modules['json'] = json
