import sys
import redisbridge
import monitor
import json
import time


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("need a json config file")
    else:
        config_file = sys.argv[1]

    with open(config_file) as f:
        config = json.load(f)
    if config.get('monitor'):
        print 'config monitor'
        monitor.main(config_file, wait=False)
    if config.get('bridge'):
        print 'config bridge'
        redisbridge.main(config_file, wait=False)

    while True:
        time.sleep(1)
