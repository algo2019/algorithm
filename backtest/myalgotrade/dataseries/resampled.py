from myalgotrade import resamplebase
from pyalgotrade.dataseries import resampled

class ResampledBarDataSeries(resampled.ResampledBarDataSeries):

    def __onNewValue(self, dataSeries, dateTime, value):
        resamplebase.addToTradingDate(dateTime)
        if _DSResampler__range is None:
            _DSResampler__range = resamplebase.build_range(dateTime, _DSResampler__frequency)
            _DSResampler__grouper = self.buildGrouper(_DSResampler__range, value, _DSResampler__frequency)
        elif _DSResampler__range.belongs(dateTime):
            _DSResampler__grouper.addValue(value)
        else:
            self.appendWithDateTime(_DSResampler__grouper.getDateTime(), _DSResampler__grouper.getGrouped())
            _DSResampler__range = resamplebase.build_range(dateTime, _DSResampler__frequency)
            _DSResampler__grouper = self.buildGrouper(_DSResampler__range, value, _DSResampler__frequency)

class ResampledDataSeries(resampled.ResampledDataSeries):

    def __onNewValue(self, dataSeries, dateTime, value):
        resamplebase.addToTradingDate(dateTime)
        if _DSResampler__range is None:
            _DSResampler__range = resamplebase.build_range(dateTime, _DSResampler__frequency)
            _DSResampler__grouper = self.buildGrouper(_DSResampler__range, value, _DSResampler__frequency)
        elif _DSResampler__range.belongs(dateTime):
            _DSResampler__grouper.addValue(value)
        else:
            self.appendWithDateTime(_DSResampler__grouper.getDateTime(), _DSResampler__grouper.getGrouped())
            _DSResampler__range = resamplebase.build_range(dateTime, _DSResampler__frequency)
            _DSResampler__grouper = self.buildGrouper(_DSResampler__range, value, _DSResampler__frequency)
