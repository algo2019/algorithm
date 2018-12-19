import datetime
import cPickle as pickle
import json, sys, os
import re


sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))
import tools
tools.use_pylib()

from Common.Dao.DBDataDao import DBDataDao


def type_p(*prices):
    return type_num(prices, 9999999.999)


def type_num(prices, uplimit):
    return map(lambda price: (lambda x: x if x < uplimit else -1)(round(float(price), 3)), prices)


def symbol(ins):
    return re.sub(r'\d', '', ins)

class DayDataSaveOpr(DBDataDao):
    def __init__(self):
        super(DayDataSaveOpr, self).__init__()

    def _insert_list(self, sql, l):
        for i in xrange(100000000):
            if i * 999 >= len(l):
                break
            try:
                tsql = sql + ','.join(map(lambda x: "('" + "','".join(map(str, x)) + "')", l[i * 999:(i + 1) * 999]))
                self.run_sqls(tsql, res=False)
                self._conn.commit()
            except:
                raise

    def update(self, instruments):
        from Common.Dao.TickDataDao import TickDataDao
        tdao = TickDataDao()
        rl = []
        res = {}
        tradingday = ''.join(str(datetime.datetime.now().date()).split('-'))
        for code in instruments:
            bar = tdao.get(code)
            code, tdate = bar['InstrumentID'], bar['TradingDay']
            if tdate != tradingday:
                continue
            open, high, low, close = type_p(bar['OpenPrice'], bar['HighestPrice'], bar['LowestPrice'],
                                            bar['ClosePrice'])
            volume, (amount,) = int(bar['Volume']), type_num((bar['Turnover'],), 99999999999999999.999)
            pre_close, avg, settle, per_settle = type_p(bar['PreClosePrice'], amount / volume if not volume == 0 else 0,
                                                        bar['SettlementPrice'], bar['PreSettlementPrice'])
            limit_up, limit_down = type_p(bar['UpperLimitPrice'], bar['LowerLimitPrice'])
            open_inter, exchange_id = int(float(bar['OpenInterest'])), bar['ExchangeID']
            chg = close - pre_close
            chg_rt, = type_p(chg / pre_close) if not pre_close == 0 else 0
            update_time = datetime.datetime.now()

            rl.append((code, tdate, open, high, low, close, pre_close, avg, settle, per_settle, volume, amount,
                       limit_up, limit_down, open_inter, chg, chg_rt, update_time, exchange_id))

            s = symbol(code)
            if res.get(s) is None:
                res[s] = (0, None, None, None)
            if volume > res[s][0]:
                res[s] = (volume, code, tdate, exchange_id)

        sql = '''INSERT INTO DayData (CODE, TDATE, OPENPRICE, HIGHPRICE, LOWPRICE, CLOSEPRICE, PERCLOSEPRICE, AVGPRICE, 
                  SETTLEPRICE, PERSETTLEPRICE, VOLUME, AMOUNT, LIMITUP, LIMITDOWN, OPENINTERPRIST, CHG, CHGRT, 
                  UPDATETIME, EXCHANGEID) 
                  VALUES'''
        self._insert_list(sql, rl)

        last_main_sql = '''SELECT SYMBOL, CODE FROM MainContract WHERE TDATE IN (SELECT max(TDATE) FROM MainContract)'''
        last_main = {x[0]: x[1] for x in self.run_sqls(last_main_sql)}

        main_sql = '''INSERT INTO MainContract(SYMBOL, TDATE, CODE, EXCHANGEID) VALUES'''
        self._insert_list(main_sql, [(k, res[k][2], max(res[k][1], last_main.get(k, k)), res[k][3]) for k in res if
                                     res[k][1] is not None])

def update_trading_day(dop):
    from Common.Dao.TickDataDao import TickDataDao
    last_day = dop.tdaysoffset(10) + dop.tdaysoffset(-10)
    if len(last_day) == 0:
        last_day = None
    else:
        last_day = ''.join(str(last_day[-1]).split('-'))

    all_tick = TickDataDao().get('*')
    for ins in all_tick:
        if all_tick[ins].TradingDay > last_day:
            dop.add_trading_day(datetime.date(
                *map(lambda x: int(x), [
                    all_tick[ins].TradingDay[:4],
                    all_tick[ins].TradingDay[4:6],
                    all_tick[ins].TradingDay[6:]])
            ))
            dop.commit()
            last_day = all_tick[ins].TradingDay


def main():
    dao = DayDataSaveOpr()
    fn = 'ins_list.pickle'

    from Common.CommonLogServer.RedisLogService import PublishLogCommand
    from Common.AtTimeObjectEngine import ThreadEngine, BaseExceptionHandler

    class ExceptionHandler(BaseExceptionHandler):
        def process(self, engine, cmd, e):
            import traceback
            PublishLogCommand('DayDataOpr', 'DayDataOpr', 'DayDataOpr', 'ERR', 'DayDataOpr',
                              traceback.format_exc()).execute()

    def _exit_process():
        PublishLogCommand('DayDataOpr', 'DayDataOpr', 'DayDataOpr', 'ERR', 'DayDataOpr', "Exit!").execute()

    import atexit

    atexit.register(_exit_process)

    _engine = ThreadEngine()
    _engine.set_running_exception_handler(ExceptionHandler())

    from Common.Command import Command, IntervalCommand, IntervalDateTimeCommand

    def record_trading_codes():
        import client
        import package_config

        with open(package_config.get_conf()['mk_configs'], 'r') as f:
            conf = json.load(f)

        if dao.is_trading_day():
            with open(fn, 'w') as f:
                pickle.dump(
                    client.PyInstrumentsGetter(
                        conf['trade_host'], conf['broker_id'], conf['investor_id'], conf['investor_password']).get_all_instruments(), f)


    IntervalCommand(60*5 , Command(target=update_trading_day, args=(dao, )), _engine)

    IntervalDateTimeCommand(datetime.time(15), Command(target=record_trading_codes), _engine)

    def update_db():
        if dao.is_trading_day():
            with open(fn, 'r') as f:
                dao.update(pickle.load(f))

    IntervalDateTimeCommand(datetime.time(16), Command(target=update_db), _engine)

    _engine._started = True
    _engine.run()


if __name__ == '__main__':
    main()
