import os, sys, socket
import time
import cPickle as pickle
from PeriodDataCache import PeriodDataCache
from PeriodDataCache.Cacher.FileCache import FileCache
from PeriodDataCache.DataGainer.DataServerGainer import DataServerGainer
import Conf


class data_set:
    def __init__(self):
        self.ErrorCode = None
        self.Codes = None
        self.Fields = None
        self.Times = None
        self.Data = None

    def _print(self):
        _tmp = map(str, self.Times)
        print '.ErrorCode = ' + str(self.ErrorCode)
        print '.Codes = ' + str(self.Codes)
        print '.Fields = ' + str(self.Fields)
        print '.Times = ' + str(_tmp)
        print '.Data = ' + str(self.Data)


class log_mgr:
    def __init__(self):
        pass  # self.f = open('log/total.log','a')

    def wLog(self, s):
        # self.f.write('[' + time.strftime('%Y-%m-%d %X', time.localtime()) + ']' + s + '\n')
        pass  # print '[' + time.strftime('%Y-%m-%d %X', time.localtime()) + ']' + s


log = log_mgr()


class dataServer(object):
    def __init__(self, host=None, data_path=None, processes=5):
        self.data_path = data_path or Conf.DATA_PATH
        self.port = 51423
        self.host = host or Conf.DEFAULT
        self.processes = processes
        self.__BUFSIZE = 1024
        self.__OKSIZE = 2
        if Conf.DB_PATH is not None:
            from HttpClient import Client
            self.cache_client = Client()
        else:
            self.cache_client = None

    def send(self, data):
        sendStr = pickle.dumps(data, 2)
        size = len(sendStr)
        self.s.send('%100.100d' % (size))
        self.s.recv(self.__OKSIZE)
        totalsent = 0
        while totalsent < size:
            sent = self.s.send(sendStr[totalsent:totalsent + self.__BUFSIZE])
            totalsent = totalsent + sent
            self.s.recv(self.__OKSIZE)

    def recv(self):
        size = int(self.s.recv(100))
        self.s.send('ok')
        chunks = []
        bytes_recd = 0
        while bytes_recd < size:
            chunk = self.s.recv(min(size - bytes_recd, self.__BUFSIZE))
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
            log.wLog('[DataServer] [DATA] [GETTING:%2.2f%%]' % (bytes_recd * 100 / size))
            self.s.send('ok')
        return pickle.loads(''.join(chunks))

    def exchange(self, data):
        self.send(data)
        return self.recv()

    def run(self, cmd, pram):
        return self.exchange([cmd + '-' + str(time.time()), pram])

    def data(self, ds):
        d = data_set()
        if ds[:3] == 'msg':
            raise Exception(str(ds))
        d.ErrorCode = ds[0]
        d.Codes = ds[1]
        d.Fields = ds[2]
        d.Times = ds[3]
        d.Data = ds[4]
        if d.ErrorCode != 0:
            log.wLog('[DataServer] [ERR] [msg:%s]' % (str(ds[4][0])))
        return d

    def start(self, p=None):
        if p != None:
            self.port = p
        if self.cache_client:
            self.cache_client.start()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.wLog('[DataServer] [INIT] [ip:%s port: %d]' % (self.host, self.port))
        self.s.connect((self.host, self.port))

    def stop(self):
        try:
            if self.cache_client:
                self.cache_client.stop()
            self.send(['over'])
        except:
            pass

    def _is_cache(self, arg):
        if not Conf.CACHE:
            return False
        if type(arg[0].get('fields')) in (list, tuple):
            fields = ','.join(arg[0].get('fields'))
        else:
            fields = arg[0].get('fields')
        return len(arg) == 1 and arg[0].get('dataName') == 'data' and fields == 'open,high,low,close,volume'

    def wmm(self, *args):
        if self.cache_client is not None:
            try:
                return self.cache_client.wmm(*args)
            except Exception as e:
                raise
                print 'cache db err: ', e
        if self._is_cache(args):
            conf = args[0]
            pdc = PeriodDataCache(FileCache(self.data_path), DataServerGainer(), self.processes)
            rt = []
            for code in conf['code'].split(','):
                conf['code'] = code
                rt += pdc.get_data(conf)
            return rt
        res = self.run('wmm', (args[0],))
        if type(res) == str:
            raise Exception(res[3:])
        return res[1]

    def wsd(self, *arg):
        return self.data(self.run('wsd', arg))

    def wss(self, *arg):
        return self.data(self.run('wss', arg))

    def wsi(self, *arg):
        return self.data(self.run('wsi', arg))

    def wst(self, *arg):
        return self.data(self.run('wst', arg))

    def wsq(self, *arg):
        return self.data(self.run('wsq', arg))

    def wset(self, *arg):
        return self.data(self.run('wset', arg))

    def weqs(self, *arg):
        return self.data(self.run('weqs', arg))

    def wpf(self, *arg):
        return self.data(self.run('wpf', arg))

    def wupf(self, *arg):
        return self.data(self.run('wupf', arg))

    def tlogon(self, *arg):
        return self.data(self.run('tlogon', arg))

    def tlogout(self, *arg):
        return self.data(self.run('tlogout', arg))

    def torder(self, *arg):
        return self.data(self.run('torder', arg))

    def tcancel(self, *arg):
        return self.data(self.run('tcancel', arg))

    def tquery(self, *arg):
        return self.data(self.run('tquery', arg))

    def tdays(self, *argv):
        if self.cache_client:
            return self.cache_client.tdays(*argv)
        return self.data(self.run('tdays', argv))

    def tdaysoffset(self, *argv):
        if self.cache_client:
            return self.cache_client.tdaysoffset(*argv)
        return self.data(self.run('tdaysoffset', argv))

    def tdayscount(self, *arg):
        return self.data(self.run('tdaysoount', arg))

    def bktstart(self, *arg):
        return self.data(self.run('bktstart', arg))

    def bktquery(self, *arg):
        return self.data(self.run('bktquery', arg))

    def bktorder(self, *arg):
        return self.data(self.run('bktorder', arg))

    def bktend(self, *arg):
        return self.data(self.run('bktend', arg))

    def bktstatus(self, *arg):
        return self.data(self.run('bktstatus', arg))

    def bktsummary(self, *arg):
        return self.data(self.run('bktsummary', arg))

    def bktdelete(self, *arg):
        return self.data(self.run('bktdelete', arg))

    def bktstrategy(self, *arg):
        return self.data(self.run('bktstrategy', arg))


d = dataServer(Conf.DEFAULT)
w = dataServer('10.2.55.48')
