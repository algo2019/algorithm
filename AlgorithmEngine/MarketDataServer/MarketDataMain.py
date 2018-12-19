# -*- coding: utf-8 -*-
"""
MarketDataMain.py
"""


def main():
    import datetime
    import time
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir)))
    from MarketDataService import TickService
    from Common.AtTimeObjectEngine import ThreadEngine
    from Common.Command import IntervalTradingDayCommand, Command

    schedule_engine = ThreadEngine()
    schedule_engine.start()
    ts = TickService()
    ts.start()
    IntervalTradingDayCommand(datetime.time(20), Command(target=ts.reset), schedule_engine)
    while 1:
        time.sleep(1)


if __name__ == '__main__':
    main()
