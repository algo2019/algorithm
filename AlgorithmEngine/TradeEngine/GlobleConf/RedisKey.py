# -*- coding:utf-8 -*-
import StartConf


class Publish(object):
    @classmethod
    def KEY(cls):
        return StartConf.PublishKey

    @classmethod
    def ExternalControl(cls):
        return '%s.EXTERNAL.%s' % cls.KEY

    @classmethod
    def HeartBeat(cls, name):
        return '%s.HEARTBEAT.%s' % (cls.KEY(), name)

    @classmethod
    def RemoteStrategy(cls, strateyName='*'):
        return '%s.REMOTE_STRATEGY.%s' % (cls.KEY(), strateyName)

    @classmethod
    def RemoteCallBack(cls, strateyName='*'):
        return '%s.REMOTE_CALL_BACK.%s' % (cls.KEY(), strateyName)

    @classmethod
    def Control(cls, strategyOrName):
        if type(strategyOrName) == str:
            name = strategyOrName
        else:
            name = strategyOrName.strategy_name
        return '%s.Controller.%s' % (cls.KEY(), name)

    @classmethod
    def OnRtnOrder(cls):
        # 修改时需要与交易引擎一起修改
        return '%s.OnRtnOrder' % cls.KEY()

    @classmethod
    def OnRtnTrade(cls):
        # 修改时需要与交易引擎一起修改
        return '%s.OnRtnTrade' % cls.KEY()

    @classmethod
    def DataPre(cls):
        return 'minData'

    @classmethod
    def Data(cls, period='*', instrument='*'):
        return '%s.%s.%s' % (cls.DataPre(), period, instrument)

    @classmethod
    def RemotePosition(cls):
        return '%s.RemotePosition' % cls.KEY()

    @classmethod
    def RemoteAccount(cls):
        return '%s.Account' % cls.KEY()


class DB(object):
    class Remote(object):
        @classmethod
        def Account(cls):
            return 'RT_ACCOUNT'

    class Strategy(object):
        @classmethod
        def AutoSaveDictOfStrategy(cls, strategyName, name):
            return 'AUTO_SAVE.%s.%s' % (strategyName, name)

        @classmethod
        def Sys(cls):
            return 'sys'

        @classmethod
        def Account(cls):
            return 'account'

        @classmethod
        def Shares(cls):
            return 'shares'

        @classmethod
        def Interests(cls):
            return 'interests'

    class Web(object):
        KEY = 'WEB'

        @classmethod
        def Account(cls):
            return '%s.ACCOUNT' % cls.KEY

        @classmethod
        def Online(cls):
            return '%s.ONLINE' % cls.KEY

        @classmethod
        def Role(cls):
            return '%s.ROLE' % cls.KEY

        @classmethod
        def Strategies(cls):
            return '%s.STRATEGIES' % cls.KEY

        @classmethod
        def Boss(cls):
            return '%s.BOSS' % cls.KEY

        @classmethod
        def States(cls, strategyName, objName='*'):
            return '%s.STATES.%s.%s' % (cls.KEY, strategyName, objName)

    class Monitor(object):
        KEY = 'MONITOR'

        @classmethod
        def Account(cls):
            return '%s.ACCOUNT' % cls.KEY

        @classmethod
        def Heartbeat(cls):
            return '%s.HEARTBEAT' % cls.KEY

        @classmethod
        def ActiveOrder(cls):
            return '%s.ACTIVE_ORDER' % cls.KEY

        @classmethod
        def Position(cls):
            return '%s.POSITION' % cls.KEY

        @classmethod
        def Timeout(cls):
            return '%s.TIMEOUT' % cls.KEY

        @classmethod
        def Err(cls, strategyName):
            return '%s.%s.ERR' % (cls.KEY, strategyName)
