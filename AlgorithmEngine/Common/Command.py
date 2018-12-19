# -*- coding: utf-8 -*-
"""
Commands
"""
import abc
import time
import datetime

from Common.utility import TradingTime


class BaseCommand(object):
    """
    BaseCommand
    """
    @abc.abstractmethod
    def execute(self):
        # type: () -> None
        """
        command action
        """
        pass

    def exception_handle(self, e):
        # type: (Exception) -> None
        """
        handle exception in command
        :param e:
        """
        raise


class Command(BaseCommand):
    """
    Command
    """
    def __init__(self, target=None, args=(), kwargs=None, name=None):
        # type: (callable, tuple, dict, str) -> None
        super(Command, self).__init__()
        self.run_time = 0
        self.__target = target
        self.__args = args
        if kwargs is None:
            self.__kwargs = {}
        else:
            self.__kwargs = kwargs
        self.__name = name

    @property
    def name(self):
        # type: () -> str
        """
        command name
        :return: name
        """
        return self.__name

    def execute(self):
        # type: () -> None
        """
        run target
        """
        if self.__target is not None:
            self.__target(*self.__args, **self.__kwargs)


class AtTimeCommand(BaseCommand):
    """
    AtTimeCommand
        run in a special time
    """
    def __init__(self, command, engine=None):
        # type: (Command, engine) -> None
        if engine is None:
            from TradeEngine.GlobleConf import SysWidget
            engine = SysWidget.get_external_engine()

        self.run_time = 0
        self._command = command
        self._init_run_time()
        self._object_engine = engine
        self._object_engine.add_command(self)

    @abc.abstractmethod
    def _init_run_time(self):
        # type: () -> None
        raise NotImplementedError

    def execute(self):
        # type: () -> None
        """
        command action
            run target command
        """
        self._command.execute()


class SleepCommand(AtTimeCommand):
    """
    SleepCommand
        wait few seconds before running action
    """
    def __init__(self, sleep_time, command, object_engine=None):
        # type: (float, Command, object_engine) -> None
        self.__sleep_time = sleep_time
        super(SleepCommand, self).__init__(command, object_engine)

    def _init_run_time(self):
        # type: () -> None
        self.run_time = time.time() + self.__sleep_time


class IntervalCommand(SleepCommand):
    """
    IntervalCommand
        repeat an action
    """

    def __init__(self, interval, command, object_engine=None):
        # type: (float, Command, object_engine) -> None
        super(IntervalCommand, self).__init__(interval, command, object_engine)
        self.__interval = interval

    def execute(self):
        # type: () -> None
        """
        command action
            run target command and add self to the engine again
        """
        super(IntervalCommand, self).execute()
        self.run_time = time.time() + self.__interval
        self._object_engine.add_command(self)


class AtDateTimeCommand(AtTimeCommand):
    """
    AtDateTimeCommand
        run an action on a special datetime
    """

    def __init__(self, at_datetime, command, object_engine=None):
        # type: (datetime, Command, object_engine) -> None
        self.__at_datetime = at_datetime
        super(AtDateTimeCommand, self).__init__(command, object_engine)

    def _init_run_time(self):
        # type: () -> None
        self.run_time = time.mktime(self.__at_datetime.timetuple())


class IntervalDateTimeCommand(AtDateTimeCommand):
    """
    IntervalDateTimeCommand
        repeat an action in a particular datetime.time
    """

    def __init__(self, at_time, command, object_engine=None):
        # type: (datetime.time, Command, object_engine) -> None
        now = datetime.datetime.now()
        if now.time() > at_time:
            date = (now + datetime.timedelta(days=1)).date()
        else:
            date = now.date()
        self._at_time = at_time
        at_datetime = datetime.datetime.combine(date, at_time)
        super(IntervalDateTimeCommand, self).__init__(at_datetime, command, object_engine)

    def execute(self):
        # type: () -> None
        """
        command action
            run target command and add self to the engine again
        """
        super(IntervalDateTimeCommand, self).execute()
        self.repeat_self()

    def repeat_self(self):
        # type: () -> None
        """
        init self again
        """
        self.__init__(self._at_time, self._command, self._object_engine)


class TradingTimeIntervalCommand(SleepCommand):
    """
    TradingTimeIntervalCommand
        repeat an action in trading time
    """

    def __init__(self, interval, command, object_engine=None):
        # type: (float, Command, object_engine) -> None
        super(TradingTimeIntervalCommand, self).__init__(interval, command, object_engine)
        self.__interval = interval

    def execute(self):
        # type: () -> None
        """
        command action
            check trading time and run target command and add self to engine again
        """
        if TradingTime.is_trading():
            super(TradingTimeIntervalCommand, self).execute()
            self.run_time = time.time() + self.__interval
        else:
            self.run_time = time.time() + TradingTime.next_trading_time_delay()
        self._object_engine.add_command(self)


class IntervalTradingDayCommand(IntervalDateTimeCommand):
    """
    IntervalTradingDayCommand
        repeat an action in a particular datetime.time when today is a trading day
    """
    def execute(self):
        # type: () -> None
        """
        command action
            check trading day and run target command and repeat self
        """
        if TradingTime.is_trading_day():
            super(IntervalTradingDayCommand, self).execute()
        else:
            self.repeat_self()
