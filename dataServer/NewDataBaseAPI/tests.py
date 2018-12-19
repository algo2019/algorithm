import datetime

from Client import TimeClientPreProcessingClient
import Client
import unittest
from tools import format_to_datetime
import copy


class ExternalFlagClientTest(unittest.TestCase):
    def setUp(self):
        self.client = TimeClientPreProcessingClient()
        self.after_conf = None
        that = self

        class MockClient(Client.BaseClient):
            def get_data(self, conf):
                if conf['dataName'] == 'tdaysoffset':
                    if conf['offset'] == -1:
                        return format_to_datetime(conf['datetime']) + datetime.timedelta(days=1)
                    if conf['offset'] == 1:
                        return format_to_datetime(conf['datetime']) - datetime.timedelta(days=1)
                that.after_conf = conf

        self.client.add_client(MockClient())

    def test(self):
        conf = {
            'dataName': 'data',
            'code': 'al1701',
            'fields': 'open,close',
            'start': '2017-01-01',
            'end': '2017-11-13',
            'tradingday': True,
        }
        self.client.get_data(copy.deepcopy(conf))
        self.assertEqual(self.after_conf['end'], datetime.datetime(2017, 11, 12, 20))
        self.assertEqual(self.after_conf['start'], datetime.datetime(2016, 12, 31, 20))

        conf['includeend'] = True
        self.client.get_data(copy.deepcopy(conf))
        self.assertEqual(self.after_conf['end'], datetime.datetime(2017, 11, 13, 20))
        self.assertEqual(self.after_conf['start'], datetime.datetime(2016, 12, 31, 20))

        conf.pop('tradingday', None)
        self.client.get_data(copy.deepcopy(conf))
        self.assertEqual(self.after_conf['end'], datetime.datetime(2017, 11, 13, 0, 0, 1))
        self.assertEqual(self.after_conf['start'], datetime.datetime(2017, 1, 1))
