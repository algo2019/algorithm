def main(path):
    import tools
    tools.use_pylib()
    import client
    import json

    with open(path, 'r') as f:
        config = json.load(f)

    config_item = {'investor_id', 'market_host', 'trade_host', 'broker_id', 'investor_password', 'redis_host',
                   'redis_port', 'publish_key'}

    for item in config_item:
        if config.get(item) is None:
            print 'error: need:', item
            print 'warn: config need items:', config_item
            exit(0)

    client.PyCSimpleHandler(config['market_host'], config['trade_host'], config['broker_id'],
                            config['investor_id'], config['investor_password'], config['redis_host'],
                            config['redis_port'], config['publish_key']).start()


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print 'need one json file as config'
        exit(0)
    main(sys.argv[1])