from pyalgotrade import bar
from OnBarData import OnBarData
from Mark import BaseMark


class Bar(OnBarData, bar.Bar, BaseMark):
    tag_dom = 0x1
    tag_instrument_last = 0x2
    tag_day_last = 0x4
    tag_day_first = 0x8

    def __init__(self, data_dict):
        OnBarData.__init__(self, data_dict)
        BaseMark.__init__(self)

    def getAdjClose(self):
        return 0

    def getOpen(self, adjusted=False):
        return self.BarOpen

    def getPrice(self):
        return self.BarClose

    def getLow(self, adjusted=False):
        return self.BarLow

    def getUseAdjValue(self):
        return False

    def getFrequency(self):
        return self.Period

    def getHigh(self, adjusted=False):
        return self.BarHigh

    def setUseAdjustedValue(self, useAdjusted):
        return True

    def getVolume(self):
        return self.BarVolume

    def getClose(self, adjusted=False):
        return self.BarClose

    def getDateTime(self):
        return self.DateTime
