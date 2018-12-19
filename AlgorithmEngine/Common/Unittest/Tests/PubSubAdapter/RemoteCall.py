import time
import unittest

from Common.ExternalCommand import RemoteCall
from Common.PubSubAdapter import RedisPubSub

__all__ = ['RemoteCallTest']


class Handler(RemoteCall.ExecutorHandler):
    def execute_cmd(self, cmd, args, temp_id):
        if cmd == 'eval':
            return eval(args)
        elif cmd == 'exec':
            import re
            exec re.sub(r'return ([^\n]*)', r'self.rt(temp_id, \1)', args)
        else:
            return 'undefine cmd'


class RemoteCallTest(unittest.TestCase):
    Executor = None
    caller = None

    def setUp(self):
        if self.Executor is None:
            ps = RedisPubSub.RedisPubSub('10.4.37.206', 6379)
            call_key = 'unittest.call'
            rt_key = 'unittest.rt'
            self.Executor = RemoteCall.Executor(ps, call_key, rt_key, Handler())
            self.Executor.start()
            self.caller = RemoteCall.Caller(ps, call_key, rt_key)

    def test_eval(self):
        self.assertEqual(self.caller.call('eval', '1+1'), 2)

    def test_exec(self):
        n = time.time()
        self.assertTrue(
            n + 0.1 < self.caller.call('exec', 'import time\ntime.sleep(0.2)\nreturn time.time()') < n + 0.3)

    def test_exec_if(self):
        run_str = 'if not hasattr(self, "_test"):\n    self._test = 0\n    return 1+1\nelse:\n    return 2+2'
        self.assertEqual(self.caller.call('exec', run_str), 2)
        self.assertEqual(self.caller.call('exec', run_str), 4)
