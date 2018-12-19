import BaseAction
import aly

class divident(BaseAction.base):
  def action(self,conf):
    cr = aly.getCodeRecognizer(aly.getList(conf['code']))
    mc = cr.getMarketCode()
    conf = {}
    rt = []
    if 'stk' in mc:
      conf['code'],conf['market'] = self.__code_market__(mc['stk'])
      rt = self.getDBA().getDataBase('gta').getDivident(conf)
      for line in rt:
        tmp = line[0]
        line[0] = cr.unRecognise('%s.%s'%(line[1],conf['market'][conf['code'].index(line[1])]))
        line[1] = tmp
    return rt

    
