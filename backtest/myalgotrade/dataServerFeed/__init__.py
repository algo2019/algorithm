# -*- coding:utf-8 -*-
import cacheFeed
import noCacheFeed
from myalgotrade.feed import Frequency
import datetime

def dataServerFeed(*arg):
    # print datetime.datetime.now(), arg
    instruments,start,end,period = arg
    try:
        return noCacheFeed.BarFeed(*arg)
    finally:
        # print datetime.datetime.now()
        pass

valid_min_frequency = set([1, 5, 10, 15, 30, 60])

def get_period_str(frequency):
    if frequency == Frequency.DAY:
        return '1d'
    minutes = int(frequency / Frequency.MINUTE)
    if minutes not in valid_min_frequency:
        Exception('not supported frequency: %s' % str(frequency))
    return '%dm'%minutes
