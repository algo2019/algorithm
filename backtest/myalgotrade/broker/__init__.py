import pyalgotrade.broker
import pyalgotrade.broker.backtesting

from myalgotrade.broker import tradeutil


class Broker(pyalgotrade.broker.backtesting.Broker):
    def __init__(self, cash, barFeed, commission=None):
        super(Broker, self).__init__(cash, barFeed, commission)
        self.__barFeed = barFeed
        self.__isOnClose = True
        self._isOnClosePrice()
    def getBarFeed(self):
        return self.__barFeed
    def setOnClosePrice(self,isOnClose):
        self.__isOnClose = isOnClose
        self._isOnClosePrice()
    def getOnClosePrice(self):
        return self.__isOnClose
    def _isOnClosePrice(self):
        if self.__isOnClose:
            from myalgotrade.broker import fillstrategy
            _strategy = fillstrategy.OnLastBarCloseFillStrategy()
        else:
            from pyalgotrade.broker import fillstrategy
            _strategy = fillstrategy.DefaultStrategy()
        self.setFillStrategy(_strategy)

    def getCash(self, includeShort=True):
        ret = self._Broker__cash
        bars = self._Broker__barFeed.getCurrentBars()
        if not includeShort and bars is not None:
            for instrument, shares in self.getPositions().iteritems():
                if shares < 0:
                    instrumentPrice = self._getBar(bars, instrument).getClose(self.getUseAdjustedValues())
                    ret += instrumentPrice * shares * tradeutil.get_trade_unit(instrument)
        return ret

    def getEquity(self):
        """Returns the portfolio value (cash + shares)."""
        ret = self.getCash()
        shares_dict = self.getPositions()
        bars = self._Broker__barFeed.getCurrentBars()
        if bars is not None:
            for instrument, shares in shares_dict.iteritems():
                price = self._getBar(bars, instrument).getClose(self.getUseAdjustedValues())
                ret += price * shares * tradeutil.get_trade_unit(instrument)

        return ret

    # Tries to commit an order execution.
    def commitOrderExecution(self, order, dateTime, fillInfo):
        price = fillInfo.getPrice()
        quantity = fillInfo.getQuantity()
        instrument = order.getInstrument()
        trade_unit = tradeutil.get_trade_unit(instrument)

        if order.isBuy():
            cost = price * quantity * -1 * trade_unit
            assert (cost < 0)
            sharesDelta = quantity
        elif order.isSell():
            cost = price * quantity * trade_unit
            assert (cost > 0)
            sharesDelta = quantity * -1
        else:  # Unknown action
            assert (False)

        commission = self.getCommission().calculate(order, price, quantity)
        cost -= commission
        resultingCash = self.getCash() + cost

        # Check that we're ok on cash after the commission.
        if resultingCash >= 0 or self._Broker__allowNegativeCash:

            # Update the order before updating internal state since addExecutionInfo may raise.
            # addExecutionInfo should switch the order state.
            orderExecutionInfo = pyalgotrade.broker.OrderExecutionInfo(price, quantity, commission, dateTime)
            order.addExecutionInfo(orderExecutionInfo)

            # Commit the order execution.
            self.setCash(resultingCash)
            updatedShares = order.getInstrumentTraits().roundQuantity(
                    self.getShares(order.getInstrument()) + sharesDelta
            )
            if updatedShares == 0:
                del self._Broker__shares[order.getInstrument()]
            else:
                self._Broker__shares[order.getInstrument()] = updatedShares

            # Let the strategy know that the order was filled.
            self.getFillStrategy().onOrderFilled(self, order)

            # Notify the order update
            if order.isFilled():
                self._unregisterOrder(order)
                self.notifyOrderEvent(
                    pyalgotrade.broker.OrderEvent(order, pyalgotrade.broker.OrderEvent.Type.FILLED, orderExecutionInfo))
            elif order.isPartiallyFilled():
                self.notifyOrderEvent(
                        pyalgotrade.broker.OrderEvent(order, pyalgotrade.broker.OrderEvent.Type.PARTIALLY_FILLED,
                                                      orderExecutionInfo)
                )
            else:
                assert (False)
        else:
            self._Broker__logger.debug("Not enough cash to fill %s order [%s] for %d share/s" % (
                order.getInstrument(),
                order.getId(),
                order.getRemaining()
            ))
