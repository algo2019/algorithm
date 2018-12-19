class WindSet:
    def __init__(self, ec=0, c=None, f=None, t=None, d=None):
        self.ErrorCode = ec
        self.Codes = c or []
        self.Fields = f or []
        self.Times = t or []
        self.Data = d or []

    def __str__(self):
        _tmp = map(str,self.Times)
        print '.ErrorCode = ' + str(self.ErrorCode)
        print '.Codes = ' + str(self.Codes)
        print '.Fields = ' + str(self.Fields)
        print '.Times = ' + str(_tmp)
        print '.Data = ' + str(self.Data)


class Adapter(object):
    def __init__(self):
        import Client as _Client
        import CacheClient as _Cache
        time_client = _Client.TimeClientPreProcessingClient()
        # tdays_client = _Client.TradingDaysClient()
        adapter_client = _Cache.AdapterClient()
        adapter_client = _Client.TradeRecordClient()
        # cache_client = _Cache.CacheDataClient()
        # cache_client.add_client(adapter_client)
        time_client.add_client('data', adapter_client)
        time_client.add_client('other', adapter_client)
        time_client.add_client('domInfo', adapter_client)
        time_client.add_client('tdays', adapter_client)
        time_client.add_client('tdaysoffset', adapter_client)
        self.client = time_client

    def start(self):
        pass

    def stop(self):
        pass

    def wmm(self, conf):
        return self.client.get_data(conf)

    def tdaysoffset(self, offset, dt=None):
        conf = {'dataName': 'tdaysoffset', 'offset': offset, 'datetime': dt}
        rt = self.wmm(conf)
        return WindSet(t=[rt], d=[[rt]])

    def tdays(self, start, end=None):
        conf = {'dataName': 'tdays', 'start': start, 'end': end}
        rt = self.wmm(conf)
        return WindSet(t=rt, d=[rt])
