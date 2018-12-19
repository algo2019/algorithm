import threading
from Common.PubSubAdapter.RedisPubSub import RedisPubSub
import time
l = threading.Lock()
key = 'tttt.sdfsf'
m = RedisPubSub('10.4.27.181', 6379)
b = RedisPubSub('10.4.37.206', 6379)


class t(object):
    last = time.time()


def send_m():
    while 1:
        time.sleep(0.5)
        if (time.time() % 20) > 10:
            continue
        m.publish(key, 'mmmmmmmmmmmmmm')


def send_b():
    while 1:
        time.sleep(0.5)
        b.publish(key, 'bbbbbbbbbbbbbbbbb')


def a(msg):
    with l:
        print 'mm'


def c(msg):
    with l:
        print 'bb'

m.subscribe(key, a)
b.subscribe(key, c)

ts = [
    threading.Thread(target=send_b),
    threading.Thread(target=send_m),
]

map(lambda t: t.setDaemon(True), ts)
map(lambda t: t.start(), ts)

while 1:
    time.sleep(1)
