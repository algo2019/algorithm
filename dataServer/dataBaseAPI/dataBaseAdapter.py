# -*- coding:utf-8 -*- 
from dataBase.GTADB import GTADB
from dataBase.choiceDB import choiceDB
import datetime
import aly
import getDataAction


# 第一层封装：
#   指数和股票日线合并
#   分钟级数据跨月查询
#   股票代码同一为 windPy 格式
#   fields 统一为 windPy 格式
class dataBase1(object):
    def __init__(self):
        self.__db = GTADB()

        # 自定义数据获取接口列表及其对照函数
        self.__dnt = {
            'divident': getDataAction.divident,
            'data': getDataAction.data,
            'domInfo': getDataAction.domInfo,
            'futs': getDataAction.futs,
            'sql': getDataAction.sqlQuery,
        }
        self.__dateFormator = aly.getDateFormator()

    def start(self):
        self.__db.start()

    def close(self):
        self.__db.close()

    def getDayData(self, sc, start, end, fields, PriceAdj, client):
        conf = {
            'client': client,
            'dataName': 'data',
            'start': start,
            'end': end,
            'code': aly.getList(sc),
            'fields': fields,
            'adj': PriceAdj,
            'period': '1d',
        }
        return self.getData(conf)

    def getMinData(self, sc, start, end, period, fields, client):
        conf = {
            'client': client,
            'dataName': 'data',
            'start': start,
            'end': end,
            'code': aly.getList(sc),
            'fields': fields,
            'period': period,
        }
        return self.getData(conf)

    # 获取交易时间序列
    def getTradeDate(self, start, end):
        return [i[0] for i in self.__db.getTradeDate({'start': self.__dateFormator.format(start, delay=1.0 / (60 * 24)),
                                                      'end': self.__dateFormator.format(end, delay=1.0 / (60 * 24))})]

    def getFutDayData(self, conf):
        return self.getMinData(conf)

    def getFutMinData(self, conf):
        return self.getMinData(conf)

    def _rt_type__(self, data, _type):
        del_set = []
        for j in range(len(data)):
            line = data[j]
            if type(line[0]) == datetime.datetime:
                line[0] = line[0].replace(microsecond=0)
                if _type == 'fut':
                    if line[0].year in {2016} and (3 <= line[0].month <= 6 or (line[0].month == 12 and 16 <= line[0].day <= 28)):
                        if line[0].date() in {datetime.date(2016, 6, 30), datetime.date(2016, 12, 28)} and line[0].time() == datetime.time(23, 59):
                            del_set.append(j)
                            continue
                        line[0] = line[0] + datetime.timedelta(minutes=1)
                    if datetime.time(5) < line[0].time() < datetime.time(9) or datetime.time(15) < line[0].time() < datetime.time(21):
                        del_set.append(j)
                        continue
            for i in range(len(line)):
                if 'Decimal' in str(type(line[i])):
                    line[i] = float(line[i])
            data[j] = list(data[j])
        while len(del_set) > 0:
            del data[del_set.pop()]

        return data

    def getDataBase(self, dataBaseName):
        dataBaseName = dataBaseName.lower()
        if dataBaseName == 'gta':
            return self.__db
        else:
            raise Exception('dataBase not exist:%s' % (dataBaseName))

    # 自定义获取数据
    def getData(self, conf):
        r = self.__dnt[conf['dataName']](self).action(conf)
        rt = self._rt_type__(r, conf.get('type'))
        # if not conf.get('orderBy'):
        #  try:
        #    rt.sort(lambda a,b:cmp(a[0],b[0]))
        #  except:
        #    pass
        return rt
