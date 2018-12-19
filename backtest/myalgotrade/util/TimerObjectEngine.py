import Queue, threading, time
from threading import Thread


class Command(object):
    def __init__(self, target=None, args=(), kwargs=None, name=None):
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
        return self.__name

    def execute(self):
        if self.__target is not None:
            self.__target(*self.__args, **self.__kwargs)

    def exception_handle(self, e):
        raise


class WaitCommand(Command):
    def __init__(self):
        super(WaitCommand, self).__init__(name='WaitCommand')
        self.event = threading.Event()

    def execute(self):
        self.event.set()

    def wait(self, *args, **kwargs):
        self.event.wait(*args, **kwargs)


class BaseTimerObjectEngine(object):
    def __init__(self, queue_class):
        self._commands = queue_class()
        self._next_commands = queue_class()
        self._new_cmd_event = threading.Condition()
        self._started = False
        self._next_run_delay = float("inf")
        self.__exception_handler = None

    @property
    def name(self):
        return 'BaseAtTimeObjectEngine'

    def _set_next_command(self):
        temp = self._commands
        self._commands = self._next_commands
        self._next_commands = temp
        self._next_run_delay = float('inf')

    def add_command(self, command):
        if not hasattr(command, 'execute'):
            raise Exception('ActiveObjectEngine add command no attr execute:%s' % str(command))
        if not hasattr(command, 'run_time'):
            command.run_time = 0
        self._new_cmd_event.acquire()
        self._add_and_update_delay(command)
        self._new_cmd_event.notify_all()
        self._new_cmd_event.release()
        return self

    def _add_and_update_delay(self, cmd):
        self._next_commands.put(cmd)
        self._next_run_delay = min(cmd.run_time - time.time(), self._next_run_delay)

    def run(self):
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
                        try:
                            cmd.exception_handle(e)
                        except Exception as e:
                            if self.__exception_handler is not None:
                                self.__exception_handler(e)
                            else:
                                raise

            if not self._started:
                break
            self._new_cmd_event.acquire()
            self._new_cmd_event.wait(self._next_run_delay)
            self._set_next_command()
            self._new_cmd_event.release()
        return self

    def set_running_exception_handler(self, handler):
        self.__exception_handler = handler

    def command_num(self):
        return self._commands.qsize() + self._next_commands.qsize() - 1


class ThreadEngine(BaseTimerObjectEngine):

    def __init__(self, name='ThreadEngine'):
        super(ThreadEngine, self).__init__(Queue.Queue)
        self._name = name
        self._thread = None

    def start(self):
        if self._started:
            return
        self._started = True
        self._thread = Thread(target=self.run, name=self._name)
        self._thread.setDaemon(True)
        self._thread.start()
        return self

    @property
    def name(self):
        return self._name

    def stop(self):
        self._started = False
        return self


class EnginePool(object):
    def __init__(self, engine_num):
        self.__engine_num = engine_num
        self.__engines = [ThreadEngine('EnginePool.{}'.format(i)) for i in xrange(engine_num)]
        self.__count = 0
        self.__queue = Queue.Queue()

    def add_command(self, command):
        self.__queue.put(command)

    def __execute(self, engine):
        cmd = self.__queue.get()
        engine.add_command(cmd)
        engine.add_command(Command(target=self.__execute, args=(engine,)))

    def start(self):
        for e in self.__engines:
            e.start()
            e.add_command(Command(target=self.__execute, args=(e,)))

    def stop(self):
        for e in self.__engines:
            e.stop()
