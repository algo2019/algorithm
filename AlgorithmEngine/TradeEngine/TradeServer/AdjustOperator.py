# -*- coding:utf-8 -*-

from TradeEngine.GlobleConf import AdjustConf
from TradeEngine.GlobleConf import AdjustStateV
from TradeEngine.GlobleConf import OffSet, StrategyWidget, SysWidget
from TradeEngine.GlobleConf import Shares
from TradeEngine.GlobleConf import Sys
from TradeEngine.GlobleConf import SysEvents, TradeSide
from TradeEngine.GlobleConf.AdjustStateV import AdjustState
from TradeEngine.MonitorClient import Monitor
from TradeEngine.ctp_trade_engine import InsertArgs

STATE = 0
FINALE_SHARE = 1
REMAIN_TIMES = 2


class AdjustOperator(object):
    def __init__(self):
        self.__strategy_name = 'AdjustOperator'
        self.__logger = Monitor.get_server_log(self.__strategy_name)
        self.__mapper = SysWidget.get_local_remote_ref_mapper()
        self.strategy_ins_obj_map = {}
        self.__states = {}
        self.__started = False

    def start(self):
        if not self.__started:
            self.__started = True
            SysEvents.OrderOver.subscribe(self.__order_over)
        return self

    def stop(self):
        if self.__started:
            self.__started = False
            SysEvents.OrderOver.unsubscribe(self.__order_over)

    @property
    def strategy_name(self):
        return self.__strategy_name

    def adjust_to(self, strategy_name, obj_name, instrument, volume, retry_times):
        Sys.time_profile_init(strategy_name, obj_name, 'adjust_to')
        strategy_name = str(strategy_name)
        self.strategy_ins_obj_map['{}.{}'.format(strategy_name, instrument)] = obj_name
        if self.__states.get(strategy_name, {}).get(instrument):
            self.__logger.ERR(strategy_name, "Strategy:%s Instrument:%s is adjusting" % (strategy_name, instrument))
            return self.__states[strategy_name][instrument][STATE]
        self.__logger.INFO(strategy_name, 'Strategy:%s start adjust:%s to %d', strategy_name, instrument, volume)
        state = AdjustState(instrument, strategy_name, obj_name)
        final_shares = self.__final_shares(volume)
        if not self.__states.get(strategy_name):
            self.__states[strategy_name] = {}
        self.__states[strategy_name][instrument] = [state, final_shares, retry_times]

        self.__state_change(strategy_name, instrument, AdjustStateV.Ready)
        self.__start_close_shares(strategy_name, instrument)

        return state

    @staticmethod
    def __final_shares(volume):
        if volume < 0:
            volume = abs(volume)
            final_shares = {
                Shares.Long: 0,
                Shares.Short: volume
            }
        else:
            final_shares = {
                Shares.Long: volume,
                Shares.Short: 0
            }
        return final_shares

    def __start_close_shares(self, strategy_name, instrument):
        self.__logger.INFO(strategy_name, 'start_close_shares : %s', instrument)
        state, final_shares, times = self.__states[strategy_name][instrument]
        if self.__check_stop(strategy_name, instrument):
            return state
        rt = self.__change_shares(strategy_name, instrument, final_shares, OffSet.Close)
        if rt == 1:
            self.__state_change(strategy_name, instrument, AdjustStateV.WaitingForClose)
        elif rt == 2:
            self.__state_change(strategy_name, instrument, AdjustStateV.WaitingForClose2)
        else:
            self.__state_change(strategy_name, instrument, AdjustStateV.CloseOk)
        self.__logger.INFO(strategy_name, 'start_close_shares ok : %s', instrument)

    def __start_open_shares(self, strategy_name, instrument):
        self.__logger.INFO(strategy_name, 'start_open_shares : %s', instrument)
        state, final_shares, times = self.__states[strategy_name][instrument]
        rt = self.__change_shares(strategy_name, instrument, final_shares, OffSet.Open)
        if rt == 1:
            self.__state_change(strategy_name, instrument, AdjustStateV.WaitingForOpen)
        elif rt == 2:
            self.__state_change(strategy_name, instrument, AdjustStateV.WaitingForOpen2)
        else:
            self.__state_change(strategy_name, instrument, AdjustStateV.OpenOk)
        self.__logger.INFO(strategy_name, 'start_open_shares ok: %s', instrument)

    def __change_shares(self, strategy_name, instrument, final_shares, offset):
        rt = 0
        for l_or_s in final_shares:
            trade_volume = self.__trade_volume(l_or_s, offset, instrument, strategy_name, final_shares)
            if trade_volume > 0:
                rt += 1
                self.__trade(strategy_name, instrument, trade_volume, l_or_s, offset)
        return rt

    def __trade(self, strategy_name, instrument, trade_volume, l_or_s, offset):
        self.__logger.INFO(strategy_name, 'start trade %s offset:%s %d', instrument, offset, trade_volume)
        client = SysWidget.get_trade_client()
        trade_side = self.__get_trade_side(l_or_s, offset)
        insert_args = InsertArgs(strategy_name, self.strategy_name, instrument, offset, trade_side,
                                 trade_volume, time_out=AdjustConf.TimeOut)
        client.insert_order(insert_args)

    @staticmethod
    def __get_trade_side(l_or_s, offset):
        if (l_or_s == Shares.Long and offset == OffSet.Open) or (
                        l_or_s == Shares.Short and offset in (OffSet.CloseToday, OffSet.Close)):
            return TradeSide.Buy
        else:
            return TradeSide.Sell

    def __state_change(self, strategy_name, instrument, state):
        _state = self.__states[strategy_name][instrument][STATE]
        _state.STATE = state
        if state == AdjustStateV.Ready:
            self.__logger.INFO(strategy_name, '%s adjust state ready', instrument)
            SysEvents.AdjustStateChange.emit(_state)
        elif state == AdjustStateV.CloseOk:
            Sys.time_profile(strategy_name, _state.obj_name, 'adjust_to', 'close_ok')
            self.__logger.INFO(strategy_name, '%s adjust state close ok', instrument)
            SysEvents.AdjustStateChange.emit(_state)
            self.__start_open_shares(strategy_name, instrument)
        elif state in AdjustStateV.NextReady:
            self.__logger.INFO(strategy_name, '%s adjust state in next ready', instrument)
            SysEvents.AdjustStateChange.emit(_state)
            del self.__states[strategy_name][instrument]
            Sys.time_profile_end(strategy_name, _state.obj_name, 'adjust_to')
        else:
            self.__logger.INFO(strategy_name, '%s adjust state %s', instrument, AdjustStateV.to_string(state))

    @staticmethod
    def __trade_volume(l_or_s, offset, instrument, strategy_name, final_shares):
        share_mgr = StrategyWidget.get_shares_mgr(strategy_name)
        if share_mgr.get_shares(instrument, l_or_s) - final_shares[l_or_s] > 0 and offset == OffSet.Close:
            return share_mgr.get_shares(instrument, l_or_s) - final_shares[l_or_s]
        if final_shares[l_or_s] - share_mgr.get_shares(instrument, l_or_s) and offset == OffSet.Open:
            return final_shares[l_or_s] - share_mgr.get_shares(instrument, l_or_s)
        return 0

    def __check_stop(self, strategy_name, instrument):
        state, final_shares, times = self.__states[strategy_name][instrument]
        if state.STATE == AdjustStateV.Stopping:
            state.STATE = AdjustStateV.Stoped
            return True
        elif state.STATE == AdjustStateV.Failed:
            return True
        return False

    def __order_over(self, order):
        if self.__mapper.get_strategy_object_name(order.order_ref) != self.strategy_name:
            return

        if self.__check_stop(self.__mapper.get_strategy_name(order.order_ref),
                             self.__mapper.get_instrument(order.order_ref)):
            return

        if order.is_filled():
            self.__on_order_ok(order)
        else:
            self.__on_canceled(order)

    def __on_order_ok(self, order):
        strategy_name = order.strategy_name
        instrument = order.instrument
        self.__logger.INFO(strategy_name, '__on_order_ok : %s', instrument)

        strategy_object_name = self.__mapper.get_strategy_object_name(order.order_ref)
        state = self.__states[strategy_name][instrument][STATE]

        if state.STATE == AdjustStateV.WaitingForClose:
            self.__logger.INFO(strategy_name, 'Strategy:%s %s instrument:%s CloseOk', strategy_name, strategy_object_name, instrument)
            self.__state_change(strategy_name, instrument, AdjustStateV.CloseOk)
        elif state.STATE == AdjustStateV.WaitingForClose2:
            self.__logger.INFO(strategy_name, 'Strategy:%s %s instrument:%s WaitingForClose', strategy_name, strategy_object_name, instrument)
            self.__state_change(strategy_name, instrument, AdjustStateV.WaitingForClose)
        elif state.STATE == AdjustStateV.WaitingForOpen:
            self.__logger.INFO(strategy_name, 'Strategy:%s %s instrument:%s AdjustOk', strategy_name, strategy_object_name, instrument)
            self.__state_change(strategy_name, instrument, AdjustStateV.OpenOk)
        elif state.STATE == AdjustStateV.WaitingForOpen2:
            self.__logger.INFO(strategy_name, 'Strategy:%s %s instrument:%s WaitingForOpen', strategy_name, strategy_object_name, instrument)
            self.__state_change(strategy_name, instrument, AdjustStateV.WaitingForOpen)

        return False

    def __on_canceled(self, order):
        strategy_name = order.strategy_name
        instrument = order.instrument
        self.__logger.INFO(strategy_name, '__on_order_canceled : %s', instrument)

        strategy_object_name = self.__mapper.get_strategy_object_name(order.order_ref)
        state, final_shares, times = self.__states[strategy_name][instrument]

        if times > 0:
            self.__logger.INFO(strategy_name, 'Strategy:%s %s instrument:%s Retry Times Remain : %d', strategy_name,
                               strategy_object_name, instrument, times)
            self.__states[strategy_name][instrument][REMAIN_TIMES] -= 1
        else:
            self.__logger.INFO(strategy_name, 'Strategy:%s %s instrument:%s Failed:RetryTimes To Max: %d', strategy_name,
                               strategy_object_name, instrument, times)
            self.__state_change(strategy_name, instrument, AdjustStateV.Failed)
            return False

        self.__change_shares(strategy_name, instrument, final_shares, order.offset)
        return False

    def stop_adjust(self, strategy_name, instrument):
        self.__state_change(strategy_name, instrument, AdjustStateV.Stopping)
