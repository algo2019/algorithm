import abc
import cPickle as pickle
import threading
import time

from Common.Command import Command

TIME_OUT = 1
__OK__ = 0
__EXCEPTION__ = 1
__MISSING_RES__ = 2
__LAST_CALL_ON__ = 3


class Caller(object):
    def __init__(self, pubsub, call_key, rt_key):
        self.__ps = pubsub
        self.__call_key = call_key
        self.rt_key = rt_key
        
        self.__rt_events = {}
        self.__rts = {}
        self.__ps.subscribe(rt_key, self.__rev_rt)

    def call(self, cmd, args):
        tid = time.time()
        rt_event = threading.Event()
        self.__rt_events[tid] = rt_event
        self.__rts[tid] = (__MISSING_RES__, None)
        rt_event.clear()
        self.__ps.publish(self.__call_key, pickle.dumps((tid, cmd, args), 2))
        rt_event.wait(TIME_OUT)
        self.__rt_events.pop(tid, None)
        return self.__return(tid)

    def __rev_rt(self, data):
        tid, state, rt = pickle.loads(data['data'])
        rt_event = self.__rt_events.get(tid)
        if rt_event is not None:
            self.__rts[tid] = (state, rt)
            rt_event.set()
            self.__rt_events.pop(tid, None)

    def __return(self, tid):
        rt = self.__rts.get(tid)
        self.__rts.pop(tid, None)
        assert rt is not None
        if rt[0] == __OK__:
            return rt[1]
        elif rt[0] == __MISSING_RES__:
            raise Exception('MISSING_RES')
        elif rt[0] == __EXCEPTION__:
            raise Exception(rt[1])
        else:
            raise Exception('unknown state:%s' % str(rt[0]))


class Executor(object):
    def __init__(self, pubsub, call_key, rt_key, executor_handler, engine=None):
        self.__ps = pubsub
        self.__call_key = call_key
        self.__rt_key = rt_key
        self.__handler = executor_handler
        self.__handler.register(self)
        self.__engine = engine

    def __rev_cmd(self, data):
        if self.__engine is not None:
            self.__engine.add_command(
                Command(name='Executor.Cmd', target=self.__execute, args=pickle.loads(data['data'])))
        else:
            self.__execute(*pickle.loads(data['data']))

    def __execute(self, temp_id, cmd, args):
        try:
            self.send_rt(temp_id, self.__handler.execute_cmd(cmd, args, temp_id))
        except:
            import traceback
            self.send_err(temp_id, traceback.format_exc())

    def send_rt(self, temp_id, rt):
        self.__ps.publish(self.__rt_key, pickle.dumps((temp_id, __OK__, rt), 2))

    def send_err(self, temp_id, err_msg):
        self.__ps.publish(self.__rt_key, pickle.dumps((temp_id, __EXCEPTION__, err_msg), 2))

    def start(self):
        self.__ps.subscribe(self.__call_key, self.__rev_cmd)

    def stop(self):
        self.__ps.unsubscribe(self.__call_key, self.__rev_cmd)


class ExecutorHandler(object):
    __metaclass__ = abc.ABCMeta

    def register(self, executor):
        self.__executor = executor

    def rt(self, temp_id, rt):
        self.__executor.send_rt(temp_id, rt)

    def send_err(self, temp_id, err_msg):
        self.__executor.send_err(temp_id, err_msg)

    @abc.abstractmethod
    def execute_cmd(self, cmd, args, temp_id):
        raise NotImplementedError
