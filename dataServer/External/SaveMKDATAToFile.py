import redis

HOST = "127.0.0.1"
PORT = 6379

FILE = "mkdata.log"

PUBLISH_KEY = "MKDATA.*"

r = redis.StrictRedis(HOST, PORT)
ps = r.pubsub()
ps.psubscribe(PUBLISH_KEY)

with open(FILE, 'w') as f:
    for msg in ps.listen():
        if msg['type'] != 'pmessage':
            continue
        f.write(msg['data'] + '\n')
