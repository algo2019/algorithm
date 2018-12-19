def LogService():
    from LogService import LogService
    return LogService()


def LocalLogCommand(pk, log_name, name, level, source, msg, args=tuple()):
    from LogCommands import LocalLogCommand
    return LocalLogCommand(pk, log_name, name, level, source, msg, args)


def PublishLogCommand(pk, log_name, name, level, source, msg, args=tuple()):
    from LogCommands import PublishLogCommand
    return PublishLogCommand(pk, log_name, name, level, source, msg, args)


def LogFile():
    from LogFile import LogFile
    return LogFile()


def Logger(system, name, source, log_name):
    # type: (str, str, str, str) -> Logger
    from LogCommands import Logger
    return Logger(system, name, source, log_name)


def ServiceLogger(system, source, log_name, default_name):
    from LogCommands import ServiceLogger
    return ServiceLogger(system, source, log_name, default_name)