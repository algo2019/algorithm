import datetime
from flask import blueprints, jsonify
from flask import request
from flask import url_for
from tools import format_to_datetime as format_dt
from ..LocalDataServer.DBApi import Tables
import cPickle as pickle

api = blueprints.Blueprint('api.v1.0', __name__)


_Host = '10.4.27.179'
_Port = 1433
_User = 'research'
_Passwd = 'rI2016'
_dbName = 'tempdb'


@api.route('/')
def index():
    rt = [{'dataName': 'tdaysoffset',
           'url': url_for('.tdaysoffset', _external=True)},
          {'dataName': 'tdays',
           'url': url_for('.tdays', _external=True)},
          {'dataName': 'daily',
           'url': url_for('.daily', _external=True)},
          {'dataName': 'min_data',
           'url': url_for('.min_data', _external=True)}]
    return jsonify(rt)


@api.route('/tdays')
def tdays():
    try:
        args = request.args
        return jsonify({
            'errcode': 0,
            'errmsg': 'ok',
            'res': pickle.dumps(_tdays(args.get('start', datetime.datetime.now()), args.get('end', datetime.datetime.now())))
        })
    except Exception as e:
        return jsonify({
            'errcode': 1,
            'errmsg': str(e),
            'res': pickle.dumps([])
        })


def _tdays(start, end):
    table = Tables.TradingDateTable()
    table.open()
    rt = map(format_dt, table.tdays(start, end))
    table.close()
    return rt


@api.route('/tdaysoffset')
def tdaysoffset():
    try:
        args = request.args
        return jsonify({
            'errcode': 0,
            'errmsg': 'ok',
            'res': pickle.dumps(_tdaysoffset(int(args.get('offset', 0)), args.get('datetime', datetime.datetime.now())))
        })
    except Exception as e:
        return jsonify({
            'errcode': 1,
            'errmsg': str(e),
            'res': pickle.dumps([])
        })


def _tdaysoffset(offset, start):
    table = Tables.TradingDateTable()
    table.open()
    rt = format_dt(table.tdaysoffset(offset, start))
    table.close()
    return rt


@api.route('/daily')
def daily():
    try:
        args = request.args
        symbol = args.get('symbol')
        start = args.get('start')
        if not symbol or not start:
            return jsonify({
                'errcode': 2,
                'errmsg': 'param: symbol,start,[end],[fields]',
                'res': pickle.dumps([])
            })
        end = args.get('end', datetime.datetime.now())
        fields = args.get('fields')
        return jsonify({
            'errcode': 0,
            'errmsg': 'ok',
            'res': pickle.dumps(_daily(symbol, start, end, fields))
        })
    except Exception as e:
        return jsonify({
            'errcode': 1,
            'errmsg': str(e),
            'res': pickle.dumps([])
        })


def _daily(symbol, start, end, fields):
    table = Tables.DailyDataTable()
    table.open()
    rt = table.select(symbol, start, end, fields)
    table.close()
    return rt


@api.route('/min_data')
def min_data():
    try:
        args = request.args
        symbol = args.get('symbol')
        start = args.get('start')
        period = args.get('period')
        tradingday = args.get('tradingday', 'False')
        if not symbol or not start or not period:
            return jsonify({
                'errcode': 2,
                'errmsg': 'param: symbol,period,start,[end],[fields],[tradingday]',
                'res': pickle.dumps([])
            })
        end = args.get('end', datetime.datetime.now())
        if tradingday == 'True':
            start = '{} 20:00:00'.format(_tdaysoffset(1, start).date())
            end = '{} 20:00:00'.format(format_dt(end, time=False))
        fields = args.get('fields')
        return jsonify({
            'errcode': 0,
            'errmsg': 'ok',
            'res': pickle.dumps(_min_data(symbol, period, start, end, fields))
        })
    except Exception as e:
        return jsonify({
            'errcode': 1,
            'errmsg': str(e),
            'res': pickle.dumps([])
        })


def _min_data(symbol, period, start, end, fields):
    table = Tables.MinDataTable()
    table.open()
    rt = table.select(symbol, period, start, end, fields)
    table.close()
    return rt


@api.route('/dom_info')
def dom_info():
    try:
        args = request.args
        symbol = args.get('symbol')
        start = args.get('start')
        if not symbol or not start:
            return jsonify({
                'errcode': 2,
                'errmsg': 'param: symbol,start,[end],[before],[after]',
                'res': pickle.dumps([])
            })
        end = args.get('end', datetime.datetime.now())
        after = int(args.get('after', 0))
        before = int(args.get('before', 0))

        return jsonify({
            'errcode': 0,
            'errmsg': 'ok',
            'res': pickle.dumps(_dom_info(symbol, start, end, before, after))
        })
    except Exception as e:
        return jsonify({
            'errcode': 1,
            'errmsg': str(e),
            'res': pickle.dumps([])
        })


def _dom_info(symbol_or_instrument, start, end, before, after):
    table = Tables.DomInfoTable()
    table.open()
    rt = table.select(symbol_or_instrument, start, end, before, after)
    table.close()
    for line in rt:
        line[1] = format_dt(line[1])
        line[2] = format_dt(line[2])
    return rt
