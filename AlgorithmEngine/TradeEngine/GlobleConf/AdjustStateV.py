Init = 0
Ready = 1
WaitingForClose = 2
CloseOk = 3
WaitingForOpen = 4
OpenOk = 5
Ok = 5
Stopping = 6
Stoped = 7
WaitingForClose2 = -1
WaitingForOpen2 = -2
Failed = -3
NextReady = (0, 1, 5, 7, -3)
OverStates = (5, -3)


def to_string(state):
    if state == Init:
        return 'Init'
    elif state == CloseOk:
        return 'CloseOk'
    elif state == Failed:
        return 'Failed'
    elif state == Ok:
        return 'OK'
    elif state == Ready:
        return 'Readey'
    elif state == Stoped:
        return 'Stop'
    elif state == Stopping:
        return 'Stopping'
    elif state == WaitingForClose:
        return 'WaitingForClose'
    elif state == WaitingForOpen:
        return 'WaitingForOpen'
    elif state == WaitingForClose2:
        return 'WaittingForClose2'
    elif state == WaitingForOpen2:
        return 'WaittingForOpen2'


class AdjustState(object):
    def __init__(self, instrument, strategy_name, obj_name):
        self.strategy_name = strategy_name
        self.obj_name = obj_name
        self.instrument = instrument
        self.STATE = Init
