# -*- coding:utf-8 -*-
from pyalgotrade.broker import fillstrategy
import pyalgotrade

class  OnLastBarCloseFillStrategy(fillstrategy.DefaultStrategy):
  """ 
  fillStrategy
  使用上一个bar的收盘价进行成交
  注意：此策略会使得 order 的 fillOnClose 选项失效
        此策略不会修改 order 的 AcceptDateTime ，因此 AcceptDateTime 与 price 所在日期不符
  """
  def fillMarketOrder(self, broker_, order, bar):
        bar = broker_.getBarFeed().getDataSeries(order.getInstrument())[-2]
        # Calculate the fill size for the order.
        fillSize = self._DefaultStrategy__calculateFillSize(broker_, order, bar)
        if fillSize == 0:
            broker_.getLogger().debug(
                "Not enough volume to fill %s market order [%s] for %s share/s" % (
                    order.getInstrument(),
                    order.getId(),
                    order.getRemaining()
                )
            )
            return None

        # Unless its a fill-on-close order, use the open price.
        price = bar.getClose(broker_.getUseAdjustedValues())
        assert price is not None

        # Don't slip prices when the bar represents the trading activity of a single trade.
        if bar.getFrequency() != pyalgotrade.bar.Frequency.TRADE:
            price = self._DefaultStrategy__slippageModel.calculatePrice(
                order, price, fillSize, bar, self.getVolumeUsed()[order.getInstrument()]
            )
        return fillstrategy.FillInfo(price, fillSize)


