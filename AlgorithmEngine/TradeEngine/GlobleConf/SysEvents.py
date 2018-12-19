from Common.Event import MarkEvent as Event

OnTickData = Event()
Publish = Event()
TradingTimeEvent = Event()
AdjustStateChange = Event()
OrderOver = Event()
OTHER_EVENTS = {}
MonitorMsgEvent = Event()


def Register(name, event):
    OTHER_EVENTS[name] = event


def Subscribe(name, func):
    OTHER_EVENTS[name].subscribe(func)
