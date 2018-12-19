import unittest

import time

from Common.AtTimeObjectEngine import ThreadEngine
from Common.Command import SleepCommand, Command

__all__ = ['SleepCommandTest']


class SleepCommandTest(unittest.TestCase):
    max_try = 5

    def __execute(self):
        self.command_execute = True

    def test_sleep(self):

        self.command_execute = False
        ae = ThreadEngine()
        ae.start()
        start = time.time()
        expect = 0.01
        SleepCommand(expect, Command(target=self.__execute), ae)
        for i in range(self.max_try):
            if self.command_execute:
                break
            time.sleep(expect)
        stop = time.time()
        self.assertTrue(self.command_execute)
        self.assertTrue(expect <= stop - start <= expect + 0.1)

