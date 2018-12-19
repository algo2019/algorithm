import unittest
from Common.PubSubAdapter.RedisPubSub import RedisPubSub
import threading
from Common.Event import Event

errs_event = Event()

__all__ = ['PubSubTest']


class PubSubTest(unittest.TestCase):
    pubsub = None
    event = {}
    err_num = 0

    def setUp(self):
        self.rt_data = {}
        if self.pubsub is None:
            self.pubsub = RedisPubSub('10.4.37.206', 6379)
        self.pubsub.set_running_exception_handler(errs_event.emit)
        errs_event.subscribe(self.my_err)

    def tearDown(self):
        errs_event.unsubscribe(self.my_err)

    def wait(self, key):
        self.event[key].wait(0.1)
        self.event[key].clear()

    def get_sub_func(self, key):
        self.event[key] = threading.Event()

        def sub_func(data):
            self.event[key].set()
            self.rt_data[key] = data['data']

        return sub_func

    def my_err(self, msg):
        self.err_num += 1

    def test_func_sub_one(self):
        pub_key = 'unittest'
        msg = 't13124'
        sub_func = self.get_sub_func(1)
        self.pubsub.subscribe(pub_key, sub_func)
        self.pubsub.publish(pub_key, msg)
        self.wait(1)
        self.assertEqual(self.rt_data[1], msg)
        self.pubsub.unsubscribe(pub_key, sub_func)

    def test_func_sub_more(self):
        pub_key = 'unittest'
        msg = '345345'
        sub_func1 = self.get_sub_func(1)
        sub_func2 = self.get_sub_func(2)
        self.pubsub.subscribe(pub_key, sub_func1)
        self.pubsub.subscribe(pub_key, sub_func2)
        self.pubsub.publish(pub_key, msg)
        self.wait(1)
        self.wait(2)
        self.assertEqual(self.rt_data[1], msg)
        self.assertEqual(self.rt_data[1], self.rt_data[2])
        self.pubsub.unsubscribe(pub_key, sub_func1)
        self.pubsub.unsubscribe(pub_key, sub_func2)

    def test_key_sub_more(self):
        pub_key = 'unittest'
        msg = 'dgsdger'
        pub_key2 = pub_key + pub_key
        sub_func1 = self.get_sub_func(1)
        sub_func2 = self.get_sub_func(2)
        self.pubsub.subscribe(pub_key, sub_func1)
        self.pubsub.subscribe(pub_key2, sub_func2)
        self.pubsub.publish(pub_key2, msg)
        self.wait(2)
        self.assertEqual(self.rt_data[2], msg)
        self.assertNotEqual(self.rt_data.get(1), self.rt_data[2])
        msg += msg
        self.pubsub.publish(pub_key, msg)
        self.wait(1)
        self.assertEqual(self.rt_data[1], msg)
        self.assertNotEqual(self.rt_data[1], self.rt_data[2])
        self.pubsub.subscribe(pub_key, sub_func1)
        self.pubsub.subscribe(pub_key2, sub_func2)

    def test_unsubscribe(self):
        pub_key = 'unittest'
        msg = '345345'
        sub_func1 = self.get_sub_func(1)
        sub_func2 = self.get_sub_func(2)
        self.pubsub.subscribe(pub_key, sub_func1)
        self.pubsub.subscribe(pub_key, sub_func2)
        self.pubsub.unsubscribe(pub_key, sub_func1)
        self.pubsub.publish(pub_key, msg)
        self.wait(2)
        self.assertEqual(self.rt_data[2], msg)
        self.assertNotEqual(self.rt_data.get(1), self.rt_data[2])
        self.pubsub.unsubscribe(pub_key, sub_func2)

    def test_err(self):
        pub_key = 'unittest'
        msg = 'kkkk'
        sub_func = self.get_sub_func(1)
        sub_func2 = self.get_sub_func(2)

        def err_sub_func(data):
            raise Exception('test err')

        self.pubsub.subscribe(pub_key, sub_func)
        self.pubsub.subscribe(pub_key, err_sub_func)
        self.pubsub.subscribe(pub_key, sub_func2)

        self.pubsub.publish(pub_key, msg)
        self.wait(2)
        self.assertEqual(self.err_num, 1)
        self.assertEqual(self.rt_data[1], msg)
        self.pubsub.unsubscribe(pub_key, err_sub_func)

        msg = 'sdfsdfsd'
        self.pubsub.publish(pub_key, msg)
        self.assertEqual(self.err_num, 1)
        self.wait(2)
        self.assertEqual(self.rt_data[1], msg)
        self.assertEqual(self.rt_data[2], msg)
        self.pubsub.unsubscribe(pub_key, sub_func)
        self.pubsub.unsubscribe(pub_key, sub_func2)
