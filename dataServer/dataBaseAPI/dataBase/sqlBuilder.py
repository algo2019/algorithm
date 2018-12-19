# -*- coding:utf-8 -*-
import aly

#sql 命令生成器
class sqlBuilder(object):
    def __check__(self,conf):
        if not conf.get('codeName'):
            raise Exception('sqlBuilder No codeName')
        if not conf.get('dateName'):
            raise Exception('sqlBuilder No dateName')
        if not conf.get('tableName'):
            raise Exception('sqlBuilder No tableName')

    #数据库时间格式为datetime
    def buildDateTime(self,conf):
        dateCmd = []
        if conf.get('start'):
            dateCmd.append(" %s>='%s' "%(conf['dateName'],conf['start']))
        if conf.get('end'):
            dateCmd.append(" %s<'%s' "%(conf['dateName'],conf['end']))
        return dateCmd
    #查询 code 只有一个
    def buildCode(self,conf):
        if not conf.get('code'):
            return []
        elif type(conf['code']) == list:
            tmp = []
            nomal = [ i for i in conf['code'] if not '_' in i ]
            if len(nomal):
                tmp.append(" (%s in ('%s')) "%(conf['codeName'],"','".join(nomal)))
            for code in [ i for i in conf['code'] if '_' in i]:
                tmp.append(" (%s like '%s') "%(conf['codeName'],code))
            return ["(%s)"%(' or '.join(tmp))]
        else:
            return [" %s='%s' "%(conf['codeName'],aly.getStr(conf['code']))]
    #数据库 时间格式为 datetime
    def buildSelect(self,conf,fg=1):
        if conf.get('fields'):
            if fg:
                return ["select %s,%s,%s from %s"%(conf['dateName'],conf['codeName'],conf['fields'],conf['tableName'])]
            else:
                return ["select %s from %s"%(conf['fields'],conf['tableName'])]
        else:
            return ["select * from %s"%(conf['tableName'])]
    def buildOtherWhere(self,conf):
        if conf.get('otherWhere'):
            return conf['otherWhere']
        return []
    def addOtherWhere(self,conf,cmd):
        if not conf.get('otherWhere'):
            conf['otherWhere'] = []
        if cmd not in conf['otherWhere'] :
            conf['otherWhere'].append(cmd)
    def buildOthers(self,conf):
        otherCmd = []
        if conf.get('orderBy'):
            orderKey = conf['orderBy'].split(',')
            if 'date' in orderKey:
                orderKey[orderKey.index('date')] = conf['dateName']
            if 'code' in orderKey:
                orderKey[orderKey.index('code')] = conf['codeName']
            otherCmd.append(' order by %s '%(','.join(orderKey)))
        if conf.get('groupBy'):
            otherCmd.append(' group by %s '%(conf['groupBy']))
        return otherCmd

    def build(self,conf,fg=1):
        self.__check__(conf)
        selectStr = self.buildSelect(conf,fg)
        whereDateStr = self.buildDateTime(conf)
        whereCodeStr = self.buildCode(conf)
        whereOtherStr = self.buildOtherWhere(conf)
        otherStr = self.buildOthers(conf)
        
        cmdList = selectStr + [' where %s'%(' and '.join(whereDateStr+whereCodeStr+whereOtherStr))] + otherStr
        return ' '.join(cmdList)
