from TradeEngine.TradeClient.BaseStrategy import BaseStrategy


class SST(BaseStrategy):
    t = 1
    def __init__(self, strategy_name, config, *args, **kwargs):
        super(SST, self).__init__(strategy_name, config, *args, **kwargs)
        self.info(str(self.param))

    def on_bars(self, data):
        for i in self.instruments:
            if self.t > 0:
                self.adjust_to(i, -1)
            else:
                self.adjust_to(i, 1)
        self.t = 0 - self.t