# -*- coding: utf-8 -*-
"""
RedisLogMain.py
"""


def run():
    from Common.CommonLogServer.RedisLogService import LogService

    LogService().start()

    import time
    while 1:
        time.sleep(1)

if __name__ == '__main__':
    run()
