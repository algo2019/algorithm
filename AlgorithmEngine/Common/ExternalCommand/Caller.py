# coding=utf-8
from RemoteCall import Caller

if __name__ == '__main__':
    import getopt

    def Usage():
        print 'ExternalCommand.py usage:'
        print 'python ExternalCommand.py [-h [-p]] [-k] exec_file '
        print '-h, --help: pubsub host'
        print '-p, --port: pubsub port'
        print '-k, --key: system publish key'
        print '--help: print help message.'

    def main(argv):
        try:
            opts, args = getopt.getopt(argv[1:], 'h:p:k:')
        except getopt.GetoptError, err:
            print str(err)
            Usage()
            sys.exit(2)

        if len(args) != 1:
            print 'need exec file'
            Usage()
            sys.exit(2)

        host, port, key = (None, None, None)
        for o, a in opts:
            if o in ('--help',):
                Usage()
                sys.exit(1)
            elif o in ('-h', '--host'):
                host = a
            elif o in ('-p', '--port'):
                port = a
            elif o in ('-k', '--key'):
                key = a

        if None is (host, port, key):
            print 'need -h -p -k'
            sys.exit()

        import Key
        with open(args[0], 'r') as f:
            from PubSubAdapter.RedisPubSub import RedisPubSub
            rt = Caller(RedisPubSub(host, port), *Key.get_key(key)).call(Key.EXEC, f.read())
            if rt is not None:
                print rt

    import sys
    main(sys.argv)


def get_caller(ps, pub_key):
    import Key
    return Caller(ps, *Key.get_key(pub_key))

