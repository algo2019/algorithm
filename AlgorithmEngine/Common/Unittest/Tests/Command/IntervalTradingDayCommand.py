import threading

import datetime
import unittest

from Common.AtTimeObjectEngine import ThreadEngine
from Common.Command import Command, IntervalTradingDayCommand

__all__ = ['IntervalTradingDayCommandTest']


class TestCommand(Command):
    def __init__(self):
        super(TestCommand, self).__init__()
        self.executed_event = threading.Event()
        self.executed = False
        self.executed_time = 0

    def execute(self):
        self.executed_event.set()
        self.executed = True
        self.executed_time = datetime.datetime.now()


class IntervalTradingDayCommandTest(unittest.TestCase):
    def test(self):
        ae = ThreadEngine().start()
        tc = TestCommand()
        now = datetime.datetime.now()
        at_datetime = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second + 1)
        IntervalTradingDayCommand(at_datetime.time(), tc, ae)
        tc.executed_event.wait(2)
        self.assertTrue(tc.executed)
        self.assertTrue(datetime.timedelta(seconds=-1) < (tc.executed_time - at_datetime) < datetime.timedelta(seconds=1))
        self.assertEqual(1, ae.command_num())
