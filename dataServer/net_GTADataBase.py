# -*- coding:utf-8 -*- 
import sys, os
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', 'AlgorithmEngine')))
from k import GTADataBase
import socket, time
from aly import log
import cPickle as pickle
import threading


class clientServer(threading.Thread):
    BUFSIZE = 1024
    OKSIZE = 2

    def __init__(self, s):
        self.__s = s
        self.__tid = str(time.time())
        self.__db = GTADataBase()
        threading.Thread.__init__(self)

    def mySend(self, data):
        sendStr = pickle.dumps(data, 2)
        size = len(sendStr)
        self.__s.send('%100.100d' % (size))
        self.__s.recv(clientServer.OKSIZE)
        totalsent = 0
        while totalsent < size:
            sent = self.__s.send(sendStr[totalsent:totalsent + clientServer.BUFSIZE])
            totalsent = totalsent + sent
            self.__s.recv(clientServer.OKSIZE)

    def myRecv(self):
        size = 0
        _size = ''
        while not size:
            try:
                _size = self.__s.recv(100)
                size = int(_size)
            except Exception, e:
                if _size == '':
                    raise e
        self.__s.send('ok')
        chunks = []
        bytes_recd = 0
        while bytes_recd < size:
            chunk = self.__s.recv(min(size - bytes_recd, clientServer.BUFSIZE))
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
            self.__s.send('ok')
        return pickle.loads(''.join(chunks))

    def run(self):
        log.wLog("[THREAD]\t[net_GTADataBase:clientServer]\t[id:%s thread:start]" % (self.__tid))
        res = 'ok'
        while 1:
            cmd = ''
            try:
                rt = self.myRecv()
                cmd = rt[0]
                log.wLog("[THREAD]\t[net_GTADataBase:clientServer]\t[id:%s cmd:%s start]" % (self.__tid, cmd))
                if cmd == 'over' or cmd == '':
                    break
                data = rt[1]
                ll = cmd.split('-')
                res = ''
                res = self.__db.call(ll[0], data)
                log.wLog("[THREAD]\t[net_GTADataBase:clientServer]\t[id:%s sending res]" % (self.__tid))
                self.mySend(res)
                log.wLog("[THREAD]\t[net_GTADataBase:clientServer]\t[id:%s cmd:%s over]" % (self.__tid, cmd))
            except Exception, e:
                self.mySend('msg' + str(e))
                log.wLog("[THREAD:ERR]\t[net_GTADataBase:clientServer]\t[id:%s %s:%s]" % (self.__tid, cmd, str(e)))
                if cmd == '':
                    break

        log.wLog("[THREAD]\t[net_GTADataBase:clientServer]\t[id:%s thread:over]" % (self.__tid))
        self.__db.stop()
        self.__s.close()

    def __del__(self):
        try:
            self.__db.stop()
        except:
            pass
        try:
            self.__s.close()
        except:
            pass


host = ''
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 51423
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(0)

log.wLog("[TEL]\t[net_GTADataBase:server_run]\t[port:%d server run]" % (port))

while 1:
    clientsock, clientaddr = s.accept()
    clientServer(clientsock).start()
