# coding=utf-8
from libcpp.string cimport string
import time
cdef extern from "pyrun_test.h":
    cdef void test(char **, int, IMsgProcessor*, CSimpleHandler*)

cdef extern from "InstrumnetGainer/InstrumnetGainer.h":
    cdef cppclass InstrumnetGainer:
        InstrumnetGainer(string& szAddress, string& brokerID, string& investorID, string& password)
        char** GetRes()
        void ReqAllInstrument()
        bint IsEnd()
        int Len()
        bint IsLogin()


cdef class PyInstrumentGainer:
    cdef InstrumnetGainer *ptr
    def __cinit__(self, string address, string broke_id, string investor_id, string password):
        self.ptr = new InstrumnetGainer(address, broke_id, investor_id, password)

    def __dealloc__(self):
        if self.ptr != NULL:
            del self.ptr

    def req_all_instrument(self):
        while not self.ptr.IsLogin():
            time.sleep(1)

        self.ptr.ReqAllInstrument()

        while not self.ptr.IsEnd():
            time.sleep(1)

        cdef len = self.ptr.Len()
        cdef char **res = self.ptr.GetRes()
        cdef i = 0
        print len
        return [bytes.encode(res[i]) for i in xrange(len)]


cdef extern from 'CSimpleHandler/CSimpleHandler.h':
    cdef cppclass IMsgProcessor:
        pass

    cdef cppclass CSimpleHandler:
        CSimpleHandler(string& brokerID, string& investorID, string& password, string& frontAddress);
        void InitProcess(IMsgProcessor* processor);
        void ReqInstrumentData(char** instruments, int len);


cdef extern from 'CSimpleHandler/PrintProcessor.h':
    cdef cppclass PrintProcessor:
        PrintProcessor()

cdef extern from 'CSimpleHandler/RedisProcessor.h':
    cdef cppclass RedisProcessor:
        RedisProcessor(string& host, int port, string& publish_key)
        PrintProcessor()

cdef class PyInstrumentsGetter:
    cdef InstrumnetGainer *ig_ptr

    def __cinit__(self, string trade_addr, string broke_id, string investor_id, string password):
        self.ig_ptr = new InstrumnetGainer(trade_addr, broke_id, investor_id, password)

    def get_all_instruments(self):
        while not self.ig_ptr.IsLogin():
            print '等待登录'
            time.sleep(1)
        self.ig_ptr.ReqAllInstrument()
        while not self.ig_ptr.IsEnd():
            print '等待接收所有合约'
            time.sleep(1)

        cdef int r_len = self.ig_ptr.Len()
        cdef char **res = self.ig_ptr.GetRes()
        r = []
        for i in xrange(r_len):
            r.append(res[i])
        return r

cdef class PyCSimpleHandler:
    cdef CSimpleHandler *ptr
    cdef InstrumnetGainer *ig_ptr
    cdef IMsgProcessor* pp

    def __cinit__(self, string mk_addr, string trade_addr, string broke_id, string investor_id, string password,
                  redis_host, redis_port, publish_key):
        self.ig_ptr = new InstrumnetGainer(trade_addr, broke_id, investor_id, password)
        self.ptr = new CSimpleHandler(broke_id, investor_id, password, mk_addr)
        self.pp = <IMsgProcessor*>(new RedisProcessor(redis_host, redis_port, publish_key))

    def __dealloc__(self):
        if self.ig_ptr != NULL:
            del self.ig_ptr
        if self.ptr != NULL:
            del self.ptr

    def start(self, control = None):
        if control is None:
            control = {}

        while not self.ig_ptr.IsLogin():
            print '等待登录'
            time.sleep(1)

        self.ig_ptr.ReqAllInstrument()

        while not self.ig_ptr.IsEnd():
            print '等待接收所有合约'
            time.sleep(1)

        cdef int r_len = self.ig_ptr.Len()
        cdef char **res = self.ig_ptr.GetRes()

        time.sleep(2)
        self.ptr.InitProcess(self.pp)
        self.ptr.ReqInstrumentData(res, r_len)

        while control.get('start', True):
            time.sleep(1)
