# -*- coding: utf-8 -*-
"""
AtTimeObjectEngine
"""
import Queue, threading, time
from threading import Thread
from Command import Command


class BaseExceptionHandler(object):
    """
    BaseExceptionHandler
    """
    def process(self, engine, cmd, e):
        # type: (ThreadEngine, Command, Exception) -> None
        """
        :param engine:
        :param cmd:
        :param e:
        """
        pass

    def __call__(self, engine, cmd, e):
        # type: (ThreadEngine, Command, Exception) -> None
        self.process(engine, cmd, e)


class ThreadEngine(object):
    """
    ThreadEngine
    """
    exception_handler = BaseExceptionHandler()
    __ENGINES = set()

    def __init__(self, name='ThreadEngine', sys_name='BaseSys'):
        # type: (str, str) -> None
        self._thread = None
        self._name = name
        self._sys_name = sys_name
        self._commands = Queue.Queue()
        self._next_commands = Queue.Queue()
        self._new_cmd_event = threading.Condition()
        self._started = False
        self._next_run_delay = float("inf")
        self._wait_event = threading.Event()

    @property
    def name(self):
        # type: () -> str
        """
        Engine name
        :return:
        """
        return self._name

    @property
    def sys_name(self):
        # type: () -> str
        """
        sys_name
        :return:
        """
        return self._sys_name

    def _set_next_command(self):
        # type: () -> None
        temp = self._commands
        self._commands = self._next_commands
        self._next_commands = temp
        self._next_run_delay = float('inf')

    def add_command(self, command):
        # type: (Command) -> self
        """
        :param command:
        :return:
        """
        if not hasattr(command, 'execute'):
            raise Exception('ActiveObjectEngine add command no attr execute:%s' % str(command))
        if not hasattr(command, 'run_time'):
            setattr(command, 'run_time', 0)
        self._new_cmd_event.acquire()
        self._add_and_update_delay(command)
        self._new_cmd_event.notify_all()
        self._new_cmd_event.release()
        return self

    def _add_and_update_delay(self, cmd):
        # type: (Command) -> None
        self._next_commands.put(cmd)
        self._next_run_delay = min(cmd.run_time - time.time(), self._next_run_delay)

    def run(self):
        # type: () -> self
        """
        :return:
        """
        while True:
            now = time.time()
            while not self._commands.empty():
                cmd = self._commands.get()
                if cmd.run_time > now:
                    self._add_and_update_delay(cmd)
                else:
                    try:
                        cmd.execute()
                    except Exception as e:
                        self.__exception_handler(cmd, e)

            if not self._started:
                break
            self._new_cmd_event.acquire()
            self._new_cmd_event.wait(self._next_run_delay)
            self._set_next_command()
            self._new_cmd_event.release()
        return self

    def __exception_handler(self, cmd, e):
        # type: (Command, Exception) -> None
        try:
            if hasattr(cmd, 'exception_handle'):
                cmd.exception_handle(e)
            else:
                raise
        except Exception as e:
            self.exception_handler(self, cmd, e)

    def set_running_exception_handler(self, handler):
        # type: (BaseExceptionHandler) -> None
        """
        :param handler:
        """
        self.exception_handler = handler

    def command_num(self):
        # type: () -> int
        """
        :return:
        """
        return self._commands.qsize() + self._next_commands.qsize()

    def wait(self):
        # type: () -> None
        """
        wait
        """
        self.add_command(Command(target=self._wait_event.set))
        self._wait_event.wait(0.5)
        self._wait_event.clear()

    def start(self):
        # type: () -> self
        """
        :return:
        """
        if self._started:
            return
        self._started = True
        self._thread = Thread(target=self.run, name=self._name)
        self._thread.setDaemon(True)
        self._thread.start()
        ThreadEngine.__ENGINES.add(self)
        return self

    def stop(self):
        # type: () -> self
        """
        :return:
        """
        self._started = False
        ThreadEngine.__ENGINES.remove(self)
        return self

    def is_alive(self):
        # type: () -> bool
        """
        :return:
        """
        if self._thread is None:
            return False
        return self._thread.is_alive()
