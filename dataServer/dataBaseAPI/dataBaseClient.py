# -*- coding:utf-8 -*-
from dataBaseAPI.dataBaseAdapter import dataBase1
import datetime
import aly
import redis
import cPickle as pickle

class myError:
  def __init__(self,ec=0,cd=[],fd=[],tm=None,dt=[['']]):
    self.ErrorCode = ec
    self.Codes = cd
    self.Fields = fd
    if tm == None:
      self.Times = [datetime.datetime.now()]
    else:
      self.Times = tm
    self.Data = dt
  def _print(self):
    _tmp = map(str,self.Times)
    print '.ErrorCode = ' + str(self.ErrorCode)
    print '.Codes = ' + str(self.Codes)
    print '.Fields = ' + str(self.Fields)
    print '.Times = ' + str(_tmp)
    print '.Data = ' + str(self.Data)

#仿 WindPy 接口封装
class Client:
  def start(self):
    try:
      self.codeRecognizer = aly.codeRecognizer()
      self.redis = redis.StrictRedis('10.4.37.206', db=10)
      self.close()
    except:
      raise
    self.db = dataBase1()
    self.db.start()

  def close(self):
    try:
      self.db.close()
    except:
      pass
  def stop(self):
    self.close()
  def __options__(self,options):
    context = {}
    if options != None:
      ds = options.split(';')
      for d in ds:
        if len(d) != 0:
          ws = d.split('=')
          context[ws[0].lower()] = ws[1]
    return context

  def __code_fileds_check__(self,sc,fileds):
    if type(sc) in [str, unicode]:
      sc = sc.split(',')
    if len(sc) > 1 and ',' in fileds:
      raise Exception('code and fileds too many!')
    return sc
  #返回结果格式化
  def __rt_one_stock__(self,fileds,rt):
    ttimes = []
    filedsNum = len(fileds.split(','))
    tdata = [[] for i in range(filedsNum)]

    for line in rt:
      ttimes.append(line[0])
      for i in range(filedsNum):
        try:
          tdata[i].append(line[i+2])
        except:
          tdata[i].append(None)
    return ttimes,tdata
  def __rt_stocks__(self,sc,rt):
    ttimes = []
    tdata = [[] for i in range(len(sc))]
    for line in rt:
      if line[0] not in ttimes:
        ttimes.append(line[0])
      for i in range(ttimes.index(line[0]) - len(tdata[sc.index(line[1])]) - 1):
        tdata[sc.index(line[1])].append(None)
      tdata[sc.index(line[1])].append(line[2])

    #没有数据的全部填 None
    for i in range(len(tdata)):
      if not len(tdata[i]):
        tdata[i] = [None for j in ttimes]
    return ttimes,tdata

  def wsd(self,sc,fileds,start,end=None,options=None):
    try:
      sc = self.__code_fileds_check__(sc,fileds)
      optionsList = self.__options__(options)
      if optionsList.get('priceadj') != None:
        PriceAdj = optionsList['priceadj'].lower()
      else:
        PriceAdj = '0'
      rt = self.db.getDayData(sc,start,end,fileds,PriceAdj, self)
      if len(sc) == 1:
        ttimes,tdata = self.__rt_one_stock__(fileds,rt)
      else:
        ttimes,tdata = self.__rt_stocks__(sc,rt)
      return myError(0,sc,fileds.split(','),ttimes,tdata)
    except Exception,e:
      return myError(1,sc,fileds.split(','),dt=[[str(e)]])


  def wsi(self,sc,fileds,start,end=None,options=None):
    try:
      sc = self.__code_fileds_check__(sc,fileds)
      #时间格式化
      time = [start,end]
      #周期
      optionsList = self.__options__(options)
      if optionsList.get('period') != None:
        period = '%.2d'%(int(optionsList['period']))
      elif optionsList.get('barsize') != None:
        period = '%.2d' % (int(optionsList['barsize']))
      else:
        period = '01'
      #返回结果时间格式化
      rt = self.db.getMinData(sc,time[0],time[1],period,fileds, self)
      if len(sc) == 1:
        ttimes,tdata = self.__rt_one_stock__(fileds,rt)
      else:
        ttimes,tdata = self.__rt_stocks__(sc,rt)
      return myError(0,sc,fileds.split(','),ttimes,tdata)
    except Exception,e:
      return myError(1,sc,fileds.split(','),dt=[[str(e)]])
  def tdays(self,start,end=None):
    #时间格式化
    res = self.db.getTradeDate(start,end)
    return myError(0,'','TIMES',res,[res])
  def tdaysoffset(self, offset, start=None):
    _len = max(offset, 10)
    forword = True
    if offset < 0:
      forword = False
      offset = abs(offset)
    if not start:
      start = datetime.datetime.now()
    else:
      start = aly.dateFormat(start)
    while 1:
      _len += _len
      if forword:
        res = self.tdays(start - datetime.timedelta(days=_len), start)
      else:
        res = self.tdays(start - datetime.timedelta(days=1), start + datetime.timedelta(days=_len))
      if res.ErrorCode != 0:
        return res
      if len(res.Data[0]) > offset:
        if forword:
          date = res.Data[0][-1 - offset]
        else:
          date = res.Data[0][offset]
        res.Times = [date]
        res.Data = [res.Times]
        return res

  def wmm(self,conf):
    conf['client'] = self
    if 1:#try:
      if conf.get('code'):
        conf['code'] = self.__code_fileds_check__(conf['code'],'')
      conf['start'] = conf.get('start')
      conf['end'] = conf.get('end')
      if conf.get('PriceAdj'):
        conf['adj'] = conf['PriceAdj'].lower()
      elif not conf.get('adj'):
        conf['adj'] = '0'
      else:
        conf['adj'] = conf['adj'].lower()

      dataName = conf['dataName']
      end = aly.dateFormat(conf['end'])
      fields = conf.get('fields')
      codes = conf.get('code')
      rt = self.db.getData(conf)
      if dataName == 'data' and aly.dateFormat(end).date() == datetime.datetime.now().date() and fields == 'open,high,low,close,volume':
        if rt[0][0].date() != end.date():
          for code in codes:
            if self.codeRecognizer.recogniseType(code) == 'fut':
              try:
                last_data = pickle.loads(self.redis.hget('LAST_TICK_DATA', code))
                if last_data[0].date() == end.date():
                  rt += [[last_data[0], code] + list(last_data[1:])]
              except:
                  pass
      return rt
    #except Exception,e:
    #  raise e
    return None
