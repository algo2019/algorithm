import pickle
import jrpc

from TradeEngine.GlobleConf import RemoteStrategy as Rsk, SysWidget, RedisKey, Sys
from TradeEngine.MonitorClient import Monitor
from TradeEngine.GlobleConf import AdjustStateV
from TradeEngine.GlobleConf.AdjustStateV import AdjustState


class CallBackMgr(object):
    def __init__(self, strategy_name):
        self.__strategy_name = strategy_name
        self.__value = {}

    def register(self, cmd, call_back_function):
        self.__value[cmd] = call_back_function

    def start(self):
        SysWidget.get_redis_reader().subscribe(RedisKey.Publish.RemoteCallBack(self.__strategy_name), self.rtn_process)

    def stop(self):
        SysWidget.get_redis_reader().unsubscribe(RedisKey.Publish.RemoteCallBack(self.__strategy_name), self.rtn_process)

    def rtn_process(self, msg):
        obj_name, cmd, args = pickle.loads(msg['data'])
        self.__value.get(cmd, self.__none)(obj_name, args)

    def __none(self, *args, **kwargs):
        pass


class RemoteStrategyCaller(object):
    def __init__(self, strategy_name, fk_host, fk_port):
        self.__remote_client = jrpc.service.SocketProxy(fk_port, fk_host, timeout=None)
        self.__call_back_mgr = CallBackMgr(strategy_name)
        self.__strategy_name = strategy_name
        self.__states = {}
        self.__logger = Monitor.get_logger('RemoteStrategyCaller')

    def start(self):
        self.__call_back_mgr.start()
        self.__call_back_mgr.register(Rsk.ADJUST_TO, self.__adjust_to_callback)
        self.__call_back_mgr.register(Rsk.ADJUST_STATE, self.__adjust_to_callback)
        self.__call_back_mgr.register(Rsk.STOP_STRATEGY, self.__stop_strategy)
        self.__logger.INFO('RemoteStrategyCaller started')
        return self

    def __stop_strategy(self, *args):
        Sys.Stoped = True

    def stop(self):
        self.__call_back_mgr.stop()

    def start_strategy(self, obj_name, instruments):
        self.__logger.INFO('strategy obj:%s register in FK %s', obj_name, str(instruments))
        self.__remote_client.strategy_start(self.__strategy_name, obj_name, instruments)

    def get_adjust_state(self, obj_name, instrument):
        key = '%s.%s' % (obj_name, instrument)
        if self.__states.get(key) is None:
            self.__states[key] = AdjustState(instrument, self.__strategy_name, obj_name)
        return self.__states[key]

    def adjust_to(self, obj_name, instrument, volume, max_try):
        Sys.time_profile_init(self.__strategy_name, obj_name, 'caller_adjust_to')
        rt_state = self.get_adjust_state(obj_name, instrument)
        rt_state.STATE = AdjustStateV.Init
        self.__logger.INFO('%s start adjust', instrument)
        Sys.time_profile_init(self.__strategy_name, obj_name, 'jrpc')
        self.__remote_client.adjust_to(self.__strategy_name, obj_name, instrument, volume, max_try)
        Sys.time_profile_end(self.__strategy_name, obj_name, 'caller_adjust_to')
        return rt_state

    def __adjust_to_callback(self, obj_name, state):
        self.__logger.INFO('adjust_call_back:%s %s' % (obj_name, AdjustStateV.to_string(state.STATE)))
        self.get_adjust_state(state.obj_name, state.instrument).STATE = state.STATE

    def publish_cmd(self, args):
        self.__logger.INFO('to publish:%s' % str(args))
        SysWidget.get_redis_reader().publish(RedisKey.Publish.RemoteStrategy(self.__strategy_name), pickle.dumps(args))
