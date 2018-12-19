from aly import dateFormat


class OnBarData(dict):
    def __init__(self, data):
        super(OnBarData, self).__init__(data)
        self.BarVolume = int(self['volume'])
        self.BarOpen = float(self['open'])
        self.BarClose = float(self['close'])
        self.BarHigh = float(self['high'])
        self.BarLow = float(self['low'])
        self.Period = self['period']
        self.DateTime = dateFormat(self['dateTime'])
        self.TotalVolume = int(self['Volume'])
        self.DayClose = float(self['LastPrice'])
        self.DayOpen = float(self['OpenPrice'])
        self.DayHigh = float(self['HighestPrice'])
        self.DayLow = float(self['LowestPrice'])
        self.DayVolume = int(self['Volume'])
        self.AskPrice = float(self['AskPrice1'])
        self.AskVolume = int(self['AskVolume1'])
        self.BidPrice = float(self['BidPrice1'])
        self.BidVolume = int(self['BidVolume1'])
        self.TradingDay = self['TradingDay']
        self.UpdateTime = self['UpdateTime']
        self.ExchangeID = self['ExchangeID']
        self.OpenInterest = float(self['OpenInterest'])
        self.SettlementPrice = float(self['SettlementPrice'])
        self.InstrumentID = self['InstrumentID']
        try:
            self.UpperLimitPrice = float(self['UpperLimitPrice'])
            self.LowerLimitPrice = float(self['LowerLimitPrice'])
        except:
            self.UpperLimitPrice = float('inf')
            self.LowerLimitPrice = float('-inf')

