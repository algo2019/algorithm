import time
import ctptradeengine
from pprint import pprint

ctptradeengine.init_thread()
# ctptradeengine.init_thread2()

pts = ctptradeengine.PyTradeService()


class spi(ctptradeengine.TradeServiceSpi):
    def on_rtn_order(self, rtn_order):
        print 'rtn_order'
        pprint(rtn_order)

    def on_rtn_trade_account(self, trade_account, rsp_info, rsp_id, is_last):
        print 'on_rtn_trading_account'
        pprint(trade_account)
        pprint(rsp_info)
        print rsp_id
        print is_last

    def on_rtn_trade(self, rtn_trade):
        print 'rtn_trade'
        print rtn_trade

    def on_rtn_position_detail(self, positon_detail_dict, rsq_info_dict, rsp_id, is_last):
        print rsp_id, is_last

pts.RegisterSpi(spi())
pts.start('9999', '066285', '3735261', 'tcp://180.168.146.187:10000', '10.4.37.206', 6379, 'TEST')

time.sleep(2)
print 'try to action'
# pts.ReqOrderInsert('m1709', 2654, ord('0'), ord('0'), 1, ord('2'), ord('3'), ord('1'), 12)
# print pts.ReqQryTradingAccount()
pts.ReqQryInvestorPositionDetail('')

while 1:
    print 'tick'
    time.sleep(1)
