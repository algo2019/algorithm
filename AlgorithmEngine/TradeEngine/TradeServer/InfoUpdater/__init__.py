import RecordAccountInterestsCommand
import RecordDrawDownByCloseCommand
import RecordIncomeCommand
import RecordInterestsCommand
import UpdateTradedLogCommand
import UpdateRemoteAccountCommand

from TradeEngine.MonitorClient.Monitor import get_server_log


class InfoUpdater(object):
    def __init__(self):
        self.__logger = get_server_log('InfoUpdater')
        self.__started = False
        self.__logger.INFO(msg='init')

    def start(self):
        if not self.__started:
            self.__started = True
            RecordAccountInterestsCommand.start_command()
            RecordDrawDownByCloseCommand.start_command()
            RecordInterestsCommand.start_command()
            RecordIncomeCommand.start_command()
            UpdateTradedLogCommand.start_command()
            UpdateRemoteAccountCommand.start_command()


