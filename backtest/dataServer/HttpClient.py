import datetime
import urllib2
import cPickle as pickle
from threading import Thread, Event
import Queue
from Queue import Empty
import json
import urlparse
from tools import format_to_datetime as format_dt
import time

HTTP_DB = 'http://10.4.37.198:5001/api/v1.0/'


class PoolThread(Thread):
    Stop = 0
    Wait = 1
    Running = 2
    Error = 3

    def __init__(self, id, pool):
        self.id = id
        self.pool = pool
        self.state = self.Stop
        self.event = Event()
        super(PoolThread, self).__init__(name='id:{}'.format(id))

    def run(self):
        while self.pool.started:
            try:
                self.state = self.Wait
                self.event.set()
                try:
                    target, args, kwargs = self.pool.queue.get(timeout=0.5)
                except Empty:
                    continue
                self.event.clear()
                self.state = self.Running
                target(*args, **kwargs)
            except:
                self.state = self.Error
                raise
        self.state = self.Stop


class ThreadPool(object):
    def __init__(self, num=4):
        self.threads = {i: PoolThread(i, self) for i in xrange(num)}
        map(lambda x: x.setDaemon(True), self.threads.values())
        self.queue = Queue.Queue()
        self.started = False

    def start(self):
        self.started = True
        map(lambda x: x.start(), self.threads.values())

    def stop(self):
        self.started = False

    def run(self, target, args=tuple(), kwargs=None):
        kwargs = kwargs or {}
        self.queue.put((target, args, kwargs))

    def join(self, timeout=None):
        time.sleep(0.001)
        while 1:
            map(lambda x: x.event.wait(timeout), self.threads.values())
            time.sleep(0.001)
            if False in map(lambda x: x.event.is_set(), self.threads.values()):
                continue
            else:
                break


class WindSet(object):
    def __init__(self):
        self.ErrorCode = 0
        self.Times = []
        self.Data = []

    def __str__(self):
        return '.ErrorCode:{}\n.Times:{}\n.Data:{}'.format(self.ErrorCode, self.Times, self.Data)


class Client(object):
    def __init__(self, api_url=None, thread_num=4):
        self.api_url = api_url or HTTP_DB

    def start(self):
        pass

    def stop(self):
        pass

    def tdays(self, start, end=''):
        r = urllib2.urlopen(urlparse.urljoin(self.api_url, 'tdays?start={}&&end={}'.format(
            urllib2.quote(str(start)), urllib2.quote(str(end)))))
        res = json.loads(r.read())
        if res['errcode'] != 0:
            raise Exception(res['errmsg'])

        rt = WindSet()
        rt.Times = pickle.loads(str(res['res']))
        rt.Data.append(rt.Times)
        return rt

    def tdaysoffset(self, offset, dt=None):
        dt = dt or datetime.datetime.now()
        url = urlparse.urljoin(self.api_url, 'tdaysoffset?offset={}&&datetime={}'.format(
            offset, urllib2.quote(str(dt))))
        r = urllib2.urlopen(url)
        res = json.loads(r.read())
        if res['errcode'] != 0:
            raise Exception(res['errmsg'])

        rt = WindSet()
        rt.Times = [pickle.loads(str(res['res']))]
        rt.Data.append(rt.Times)
        return rt

    def wmm(self, conf):
        if conf['dataName'] == 'domInfo':
            return self._dom_info(conf)
        if conf['dataName'] == 'data' and conf['period'] == '1d':
            return self._daily(conf)
        if conf['dataName'] == 'data' and conf['period'] != '1d':
            return self._min(conf)
        else:
            raise Exception('not support this conf!' + str(conf['dataName']))

    def _dom_info(self, conf):
        rt = []
        before = conf.get('beforeday') or conf.get('beforday') or 0
        for commodity in conf['commodity']:
            r = urllib2.urlopen(urlparse.urljoin(self.api_url, 'dom_info?symbol={}&&start={}&&end={}&&after={}&&before={}'.format(
                commodity, urllib2.quote(str(conf['start'])), urllib2.quote(str(conf['end'])), conf.get('afterday', 0),
                before)))
            res = json.loads(r.read())
            if res['errcode'] != 0:
                raise Exception(res['errmsg'])
            rt += pickle.loads(str(res['res']))
        return rt

    def _daily(self, conf):
        if conf.get('includeend', False):
            conf['end'] = format_dt(conf.get('end', datetime.datetime.now())) + datetime.timedelta(days=1)
        conf['start'] = urllib2.quote(str(conf['start']))
        conf['end'] = urllib2.quote(str(conf.get('end', '')))

        r = urllib2.urlopen(self.api_url + 'daily?symbol={}&&start={}&&end={}&&fields={}'.format(
            conf['code'], conf['start'], conf['end'], conf['fields']))
        res = json.loads(r.read())
        if res['errcode'] != 0:
            raise Exception(res['errmsg'])
        return pickle.loads(str(res['res']))

    @staticmethod
    def _month_day(dt):
        if dt.month == 12:
            return dt.replace(year=dt.year+1, month=1, day=1)
        else:
            return dt.replace(month=dt.month+1, day=1)

    def _min(self, conf):
        symbol = conf['code']
        period = conf['period']
        tradingday = conf.get('tradingday', False)
        if type(conf['fields']) in (str, unicode):
            fields = conf['fields']
        else:
            fields = ','.join(conf['fields'])
        end = format_dt(conf.get('end', datetime.datetime.now()))
        if tradingday and not conf.get('includeend', False):
            end = self.tdaysoffset(1, end).Data[0][0]
        start = conf['start']
        r = urllib2.urlopen(urlparse.urljoin(self.api_url, "min_data?tradingday={}&&period={}&&symbol={}&&start={}&&end={}&&fields={}".format(
                                                 tradingday, period, symbol, urllib2.quote(str(start)),
                                                 urllib2.quote(str(end)), fields)))
        res_ = json.loads(r.read())
        if res_['errcode'] != 0:
            raise Exception(res_['errmsg'])
        return pickle.loads(str(res_['res']))
