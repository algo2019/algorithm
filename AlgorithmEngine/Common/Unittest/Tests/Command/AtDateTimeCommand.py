import unittest

import time

import datetime

from Common.Command import AtDateTimeCommand, Command
from Common.AtTimeObjectEngine import ThreadEngine

__all__ = ['AtDateTimeCommandTest']


class AtDateTimeCommandTest(unittest.TestCase):
    max_time = 5

    def setUp(self):
        self.command_execute = False
        self.e = ThreadEngine()

    def __execute(self):
        self.command_execute = True

    def test_at_datetime(self):
        self.command_execute = False
        start = time.time()
        expect = 0.01
        self.e.start()
        AtDateTimeCommand(datetime.datetime.now() + datetime.timedelta(microseconds=expect * 1000000), Command(target=self.__execute), self.e)
        for i in range(int(self.max_time / expect) + 1):
            if self.command_execute:
                break
            time.sleep(expect)
        stop = time.time()
        self.assertTrue(self.command_execute)
        self.assertTrue(expect <= stop - start <= expect + 1)

    def _test_for_times(self):
        for i in range(1000):
            self.test_at_datetime()

