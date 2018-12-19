import datetime
from OrderUnit import OrderUnit
from TradeEngine.GlobleConf import StrategyEvent, SysEvents, Sys
from TradeEngine.GlobleConf import SysWidget
from TradeEngine.MonitorClient import Monitor
from Common.Command import Command

Engine = SysWidget.get_main_engine()


class CheckCanceledCommand(Command):
    def __init__(self, order, state):
        super(CheckCanceledCommand, self).__init__(name='CheckCanceledCommand')
        self.__order = order
        self.__state = state

    def execute(self):
        if self.__order.filled_volume < self.__order.traded_volume:
            State.WAIT_TO_CANCELED.append(self)
            self.__order.logger.INFO(self.__order.strategy_name, 'canceled wait for trade')
            self.__order.logger.INFO(self.__order.strategy_name, 'canceled get trade ok')
        else:
            self.__order.stop()
            self.__order.state_change(self.__state)
            self.__order.state.action(self.__order)


class State(object):
    SUBMITTED = 1
    ACCEPTED = 2
    PARTIALLY_FILLED = 3
    CANCELED = 4
    FILLED = 5
    WAIT_TO_CANCELED = []

    def __init__(self, state_code):
        self.__state = state_code

    def is_active(self):
        return self.__state < State.CANCELED

    def can_change_to(self, state):
        return state.state_code > self.state_code

    @property
    def string(self):
        return ''

    @property
    def state_code(self):
        return self.__state

    def on_rtn_trade(self, order):
        if order.filled_volume < order.volume and self.can_change_to(PartiallyFilled):
            order.state_change(PARTIALLY_FILLED)
            order.state.action(order)
        elif order.filled_volume == order.volume and self.can_change_to(Filled):
            order.stop()
            order.state_change(FILLED)
            order.state.action(order)
        map(Engine.add_command, self.WAIT_TO_CANCELED)

    def on_rtn_order(self, order, state):
        if self.can_change_to(state):
            if state == CANCELED:
                Engine.add_command(CheckCanceledCommand(order, state))
            else:
                order.state_change(state)
                order.state.action(order)

    def action(self, order):
        StrategyEvent.get_order_state_change(order.strategy_name).emit(order)


class Submited(State):
    def __init__(self):
        super(Submited, self).__init__(State.SUBMITTED)

    @property
    def string(self):
        return 'SUBMITTED'


class Accepted(State):
    def __init__(self):
        super(Accepted, self).__init__(State.ACCEPTED)

    @property
    def string(self):
        return 'ACCEPTED'


class PartiallyFilled(State):
    def __init__(self):
        super(PartiallyFilled, self).__init__(State.PARTIALLY_FILLED)

    def can_change_to(self, state):
        return self.state_code <= state.state_code

    @property
    def string(self):
        return 'PARTIALLY_FILLED'


class Canceled(State):
    def __init__(self):
        super(Canceled, self).__init__(State.CANCELED)

    def can_change_to(self, state):
        return False

    @property
    def string(self):
        return 'CANCELED'

    def action(self, order):
        super(Canceled, self).action(order)
        SysEvents.OrderOver.emit(order)


class Filled(State):
    def __init__(self):
        super(Filled, self).__init__(State.FILLED)

    def can_change_to(self, state):
        return False

    @property
    def string(self):
        return 'FILLED'

    def action(self, order):
        super(Filled, self).action(order)
        SysEvents.OrderOver.emit(order)


SUBMITED = Submited()
ACCEPTED = Accepted()
PARTIALLY_FILLED = PartiallyFilled()
CANCELED = Canceled()
FILLED = Filled()


class BaseOrder(OrderUnit):
    __logger = Monitor.get_server_log('BaseOrder')

    def __init__(self, order_ref, instrument, offset, trade_side, price, volume):
        super(BaseOrder, self).__init__(instrument, offset, trade_side, price, volume)
        self.order_ref = order_ref
        self.datetime = datetime.datetime.now()
        self.state = SUBMITED
        self.filled_volume = 0
        self.filled_price = 0
        self.traded_volume = 0

    @property
    def logger(self):
        return self.__logger

    @property
    def strategy_name(self):
        return SysWidget.get_local_remote_ref_mapper().get_strategy_name(self.order_ref)

    def is_active(self):
        return self.state.is_active()

    def state_change(self, state):
        self.state = state

    def is_partially_filled(self):
        return isinstance(self.state, PartiallyFilled)

    def is_accepted(self):
        return isinstance(self.state, Accepted)

    def is_filled(self):
        return isinstance(self.state, Filled)

    def is_canceled(self):
        return isinstance(self.state, Canceled)

    def copy_unit(self, **kwargs):
        init_args = []
        for key in ['order_ref', 'instrument', 'offset', 'trade_side', 'price', 'volume']:
            init_args.append(kwargs.get(key, self.__getattribute__(key)))
        rt_order = BaseOrder(*init_args)
        for key in ['filled_volume', 'filled_price', 'state', 'datetime']:
            rt_order.__setattr__(key, kwargs.get(key, self.__getattribute__(key)))
        return rt_order


class Order(BaseOrder):
    def __init__(self, order_ref, instrument, offset, trade_side, price, volume):
        super(Order, self).__init__(order_ref, instrument, offset, trade_side, price, volume)
        self.__strategy_name = self.strategy_name
        self.logger.INFO(self.__strategy_name, 'init order ref:%s %s %s %s %2.2f %d', order_ref, instrument, offset,
                         trade_side, price, volume)
        self.__order_change_event = StrategyEvent.get_order_state_change(self.__strategy_name)
        self.__last_trade = None
        self.__stoped = True
        self.start()

    def start(self):
        if self.__stoped:
            Sys.time_profile_init(self.__strategy_name, self.instrument, 'Order')
            Sys.time_profile(self.__strategy_name, self.instrument, 'TradeSide', self.trade_side)
            self.__stoped = False
            StrategyEvent.get_on_rtn_trade(self.__strategy_name).subscribe(self.__update_filled_volume)
            StrategyEvent.get_on_rtn_order(self.__strategy_name).subscribe(self.__update_rtn_order)
            SysWidget.get_active_order_list().append(self)
            self.logger.INFO(self.__strategy_name, 'ref:%s add active', self.order_ref)

    def stop(self):
        if not self.__stoped:
            self.__stoped = True
            StrategyEvent.get_on_rtn_trade(self.__strategy_name).unsubscribe(self.__update_filled_volume)
            StrategyEvent.get_on_rtn_order(self.__strategy_name).unsubscribe(self.__update_rtn_order)
            SysWidget.get_active_order_list().remove(self)
            self.logger.INFO(self.__strategy_name, 'ref:%s not active', self.order_ref)
            Sys.time_profile_end(self.__strategy_name, self.instrument, 'Order')
        return self

    @property
    def last_trade(self):
        return self.__last_trade

    def __update_filled_volume(self, trade):
        if trade.order_ref == self.order_ref:
            Sys.time_profile_init(self.__strategy_name, self.instrument, 'update_filled_volume')
            if self.filled_volume + trade.volume > self.volume:
                raise Exception('traded volume:%d > order volume:%d' % (self.filled_volume + trade.volume, self.volume))
            cost = self.filled_volume * self.filled_price + trade.volume * trade.price
            self.filled_volume += trade.volume
            if self.filled_volume != 0:
                self.filled_price = cost / self.filled_volume
            else:
                self.filled_price = 0

            self.__last_trade = trade
            self.state.on_rtn_trade(self)
            Sys.time_profile_end(self.__strategy_name, self.instrument, 'update_filled_volume')

    def __update_rtn_order(self, rtn_order, state):
        if rtn_order.order_ref == self.order_ref:
            Sys.time_profile_init(self.__strategy_name, self.instrument, 'update_rtn_order')
            self.traded_volume = rtn_order.traded_volume
            self.state.on_rtn_order(self, state)
            self.logger.INFO(self.__strategy_name, 'ref:%s order state:%s', self.order_ref, self.state.string)
            Sys.time_profile_end(self.__strategy_name, self.instrument, 'update_rtn_order')
