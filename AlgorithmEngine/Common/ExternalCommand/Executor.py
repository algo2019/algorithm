import re

import Key
from RemoteCall import Executor, ExecutorHandler


class __Handler(ExecutorHandler):

    def __init__(self):
        self.ct = {}

    def subscribe(self, key, func):
        self.ct[key] = func

    def execute_cmd(self, cmd, args, temp_id):
        that = self
        if cmd == Key.EVAL:
            exec re.sub(r'return ([^\n]*)', r'self.rt(temp_id, \1)', args)
        elif cmd == Key.EXEC:
            exec args
        elif self.ct.get(cmd) is not None:
            self.rt(temp_id, self.ct[cmd](temp_id, *args))
        else:
            self.rt(temp_id, None)
            raise Exception('undefine cmd %s' % str(cmd))

Handler = __Handler()

__Executor = None


def get_executor(ps, publish_key, engine=None):
    global __Executor
    if __Executor is None:
        k1, k2 = Key.get_key(publish_key)
        __Executor = Executor(ps, k1, k2, Handler, engine)
    return __Executor
