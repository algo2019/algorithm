class base(object):
  def __init__(self,dataBaseAdapter):
    self.__dba = dataBaseAdapter
  def getDBA(self):
    return self.__dba
  def action(self,conf):
    return []
  def __code_market__(self,stock):
    sc = []
    mk = []
    for l in stock:
      rt = l.split('.')
      sc.append(rt[0])
      if len(rt) > 1:
        mk.append(rt[1])
    return (sc,mk)
