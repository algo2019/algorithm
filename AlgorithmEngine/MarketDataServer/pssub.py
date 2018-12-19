import redis
from mkdata_tools import get_dict_data


r = redis.StrictRedis('10.4.27.182')

ps = r.pubsub()
ps.psubscribe('Control')

for msg in ps.listen():
    if msg['type'] != 'pmessage':
        continue
    # if msg['channel'].startswith('test.cccc.01'):
    print msg['channel'], msg['data'] #get_dict_data(msg)['dateTime']