import abc

from Common.Command import Command
from TradeEngine.GlobleConf import SysWidget
from Common.Event import Event


class RemoteInfoCommand(Command):
    __events = {}

    def __init__(self, call_back, publish_key, name='RemoteInfoCommand'):
        self._call_back = call_back
        if self.__events.get(publish_key) is None:
            self.__events[publish_key] = Event()
        self._sub_event = self.__events[publish_key]

        SysWidget.get_redis_reader().subscribe(publish_key, self._sub_event.emit)
        super(RemoteInfoCommand, self).__init__(name=name)

    @abc.abstractmethod
    def execute(self):
        return NotImplementedError()
