# coding=utf-8
import dataServer
import os
from myalgotrade.feed import Frequency
import myalgotrade.context
import pprint
from multiprocessing import Pool
from myalgotrade.broker import tradeutil

def get_contract_data(contract_id, frequency, start_date, end_date):
    d = dataServer.dataServer()
    d.start()
    if frequency >= Frequency.DAY:
        period = '1d'
    else:
        period = '%dm'%(int(frequency / Frequency.MINUTE))
    rows = d.wmm({
        'dataName': 'data',
        'period': period,
        'code':contract_id,
        'start':start_date,
        'end':end_date ,
        'fields':'open,high,low,close,volume' ,
        })
    d.stop()
    data = []
    for row in rows:
        data.append('%s,%s,%s,%s,%s,%s' % (row[0], row[2], row[3], row[4], row[5], row[6]))
    return data

def get_dominant_contract_infos(commodity, frequency, start_date, end_date, before_days=0, after_days=0):
    d = dataServer.dataServer()

    available_date = tradeutil.get_available_start(commodity)
    if start_date < available_date:
        start_date = available_date

    if start_date >= end_date:
        return dict()

    conf = {
        'dataName': 'domInfo',
        'start': start_date,
        'end': end_date,
        'beforday': before_days,
        'afterday': after_days,
        'commodity': commodity,
    }
    pprint.pprint(conf)
    d.start()
    result = d.wmm(conf)
    d.stop()
    ret = dict((str(i[0]),(frequency, i[1], i[2])) for i in result)
    return ret

def _get_data_async(data_infos, processes):
    ret = {}
    pool = Pool(processes)
    threads = {}
    for instrument in data_infos:
        frequency, start_datetime, end_datetime = data_infos[instrument]
        threads[instrument] = pool.apply_async(get_contract_data,(instrument, frequency, start_datetime, end_datetime))
    datas = {}
    for instrument in data_infos:
        data = threads[instrument].get()
        if data is not None:
            datas[instrument] = data
    pool.terminate()
    return datas

def get_data_from_sqlserver(data_infos, async=4):
    if async:
        return _get_data_async(data_infos, async)
    data = {}
    for instrument in data_infos:
        frequency, start_datetime, end_datetime = data_infos[instrument]
        result = get_contract_data(instrument, frequency, start_datetime, end_datetime)
        if result is not None:
            data[instrument] = result
    return data

def main():
    import datetime
    start_date = '2010-01-01'
    end_date = '2015-01-01'
    doms = get_dominant_contract_infos('M', Frequency.MINUTE, start_date, end_date, before_days=10)
    pprint.pprint(doms)
    for async_ in [4,2,0]:
        t1 = datetime.datetime.now()
        data = get_data_from_sqlserver(doms, async=async_)
        t2 = datetime.datetime.now()
        print '%d processes time:'%(async_),t2-t1

if __name__ == '__main__':
    main()
