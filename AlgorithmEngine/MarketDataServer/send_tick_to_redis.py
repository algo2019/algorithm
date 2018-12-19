import sys
import os

import datetime
import threading


def send_to_redis(file_name):
    try:
        with open(file_name, 'r') as f:
            import redis
            l = 0
            r = redis.StrictRedis('10.4.27.182')
            for line in f.xreadlines():
                r.publish('test.MKDATA.__', line.strip())
                l += 1
                if l > 10000:
                    PReady.wait()
                    l = 0
                    PReady.clear()

    except Exception as e:
        print e


def get_file_name(dt):
    return 'TickData.%s.%s' % (dt.date(), dt.hour)


PReady = threading.Event()
W_SHFReady = threading.Event()
W_DLReady = threading.Event()
W_ZZReady = threading.Event()
W_CCReady = threading.Event()


def check():
    import redis
    r = redis.StrictRedis('10.4.27.182')
    ps = r.pubsub()
    ps.psubscribe('Control')
    for msg in ps.listen():
        if msg['type'] != 'pmessage':
            continue
        if msg['data'] == 'P':
            if not PReady.is_set():
                PReady.set()
        elif msg['data'] == 'W-SHF':
            if not PReady.is_set():
                continue
            if not W_SHFReady.is_set():
                print 'W-SHF ready'
                W_SHFReady.set()
        elif msg['data'] == 'W-DL':
            if not PReady.is_set():
                continue
            if not W_DLReady.is_set():
                print 'W-DL ready'
                W_DLReady.set()
        elif msg['data'] == 'W-ZZ':
            if not PReady.is_set():
                continue
            if not W_ZZReady.is_set():
                print 'W-ZZ ready'
                W_ZZReady.set()
        elif msg['data'] == 'W-CC':
            if not PReady.is_set():
                continue
            if not W_CCReady.is_set():
                print 'W-CC ready'
                W_CCReady.set()

t = threading.Thread(target=check)
t.setDaemon(True)
t.start()


def main():
    times = [
        (datetime.datetime(2017, 3, 30, 10), datetime.datetime(2017, 4, 10, 16)),
        (datetime.datetime(2017, 4, 11, 16), datetime.datetime(2017, 4, 25, 16)),
    ]
    for start, end in times:
        cur = start
        while cur < end:
            if os.path.exists(get_file_name(cur)):
                print 'start procee for ', get_file_name(cur)
                print 'wait P and W ready'
                PReady.wait()
                W_CCReady.wait()
                W_SHFReady.wait()
                W_DLReady.wait()
                W_ZZReady.wait()
                os.system('python %s %s' % (__file__, get_file_name(cur)))
                PReady.clear()
                W_CCReady.clear()
                W_SHFReady.clear()
                W_DLReady.clear()
                W_ZZReady.clear()
            cur += datetime.timedelta(hours=1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    else:
        send_to_redis(sys.argv[1])
