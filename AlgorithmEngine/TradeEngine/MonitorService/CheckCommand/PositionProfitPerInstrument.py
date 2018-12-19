from Common.Command import Command


class PositionProfitPerInstrument(Command):
    def __init__(self, monitor_server):
        self.__monitor_server = monitor_server
        super(PositonProfitPerInstrument, self).__init__(name='CheckPositionProfitPerInstrument')

    def execute(self):
        pass
