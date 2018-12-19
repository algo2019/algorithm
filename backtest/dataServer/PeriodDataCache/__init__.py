import datetime
from Queue import Queue
import threading


class PeriodDataCache(object):
    def __init__(self, cacher, data_gainer, asyn=5):
        self.__cacher = cacher
        self.__data_gainer = data_gainer
        self.__asyn = asyn
        self.__lock = threading.Lock()

    def get_data(self, conf):
        if type(conf.get('start')) != datetime.datetime:
            import aly
            conf['start'] = aly.dateFormat(conf.get('start'))
        if type(conf.get('end')) != datetime.datetime:
            import aly
            conf['end'] = aly.dateFormat(conf.get('end'))

        datetime_queue = self._get_date_times(conf)
        res = [None for i in xrange(datetime_queue.qsize())]
        # thread_list = [threading.Thread(target=self._get_data_from_cache_or_cache_data,args=(instrument, period, tradingday, datetime_queue, res)) for i in xrange(self.__asyn)]
        # map(lambda x: x.setDaemon(True), thread_list)
        # map(lambda x: x.start(), thread_list)
        # map(lambda x: x.join(), thread_list)
        # thread_list = [threading.Thread(target=self._get_data_from_cache_or_cache_data,args=(instrument, period, tradingday, datetime_queue, res)) for i in xrange(self.__asyn)]
        self._get_data_from_cache_or_cache_data(conf, datetime_queue, res)
        return sum(res, [])

    def _get_date_times(self, conf):
        start, end = conf['start'], conf['end']
        rt = Queue()
        cur = start
        id = 0
        while cur < end:
            last_day = self._last_day_of_month(cur)
            if last_day + datetime.timedelta(seconds=1) < end:
                rt.put((id, cur, min(last_day, end), False))
            else:
                rt.put((id, cur, min(last_day, end), conf.get('includeend', False)))
            cur = last_day + datetime.timedelta(seconds=1)
            id += 1
        return rt

    @staticmethod
    def _last_day_of_month(date_time):
        if date_time.month == 12:
            return datetime.datetime(date_time.year + 1, 1, 1) - datetime.timedelta(seconds=1)
        else:
            return datetime.datetime(date_time.year, date_time.month + 1, 1) - datetime.timedelta(seconds=1)

    def _get_data_from_cache_or_cache_data(self, conf, queue, res):
        self.__lock.acquire()
        while not queue.empty():
            id, start, end, is_last = queue.get()
            self.__lock.release()
            conf['start'] = start
            conf['end'] = end
            conf['includeend'] = is_last
            rt = self._get_data_for_one(conf)
            res[id] = rt
            self.__lock.acquire()
        self.__lock.release()

    def _get_data_for_one(self, conf):
        rt = self.__cacher.get_data(conf)
        if rt is None:
            rt = self.__data_gainer.get_data(conf)
            self.__cacher.cache_data(conf, rt)
        return rt