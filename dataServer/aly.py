# -*- coding:utf-8 -*-
import re
import datetime
import time


class log_mgr:
    def __init__(self):
        pass  # self.f = open('log\\total.log','a')

    def wLog(self, s):
        # self.f.write('[' + time.strftime('%Y-%m-%d %X', time.localtime()) + ']' + s + '\n')
        print '[' + time.strftime('%Y-%m-%d %X', time.localtime()) + ']' + s


log = log_mgr()


# 品种代码识别器
class codeRecognizer(object):
    # 可接收的格式
    REG = {
        'stk': [
            [r'^(\d{6})\.(SH|SZ)$', r'\1.\2'],
            [r'^(SH|SZ)(\d{6})$', r'\2.\1'],
        ],
        'fut': [
            [r'^([A-Z]{1,2}\d{3,4})$', r'\1.ZZ'],
            [r'^([A-Z]{1,2}\d{3,4})\.([A-Z]+)$', r'\1.\2'],
        ],
        'futsymbol': [
            [r'^([a-z]{1,2}$)', r'\1'],
        ]
    }
    # 股指期货格式
    FFUTREG = [r'^((?:IF|IC|IH|T|TF)\d{4})\.([A-Z]+)$', r'\1.\2']

    def __init__(self, codes=None):
        self.__codesInfo = {}
        if codes:
            for code in codes:
                typeStr, rtcode = self.recognise(code)
                if rtcode not in self.__codesInfo:
                    self.__codesInfo[rtcode] = [code, typeStr]
                    fut_code = self.__specialCode__(rtcode)
                    if fut_code:
                        self.__codesInfo[fut_code] = [code, typeStr]

    def getCodeList(self):
        return [code for code in self.__codesInfo]

    def __specialCode__(self, code):
        reg = r'^([A-Z]{1,2})(\d{3,4})\.([A-Z]+)$'
        if re.match(reg, code):
            s1, s2, s3 = re.sub(reg, r'\1 \2 \3', code).split()
            if len(s2) == 3:
                return '%s1%s.%s' % (s1, s2, s3)
            else:
                return '%s%s.%s' % (s1, s2[1:], s3)
        return None

    def recognise(self, code):
        code = code.upper()
        for typeStr in codeRecognizer.REG:
            for reg in codeRecognizer.REG[typeStr]:
                if re.match(reg[0], code):
                    rtStr = re.sub(reg[0], reg[1], code)
                    if typeStr == 'fut':
                        if re.match(codeRecognizer.FFUTREG[0], rtStr):
                            typeStr = 'ffut'
                    elif typeStr == 'stk':
                        if rtStr in IDXLIST:
                            typeStr = 'idx'
                    return typeStr, rtStr
        raise Exception("code:%s can't be recognised" % (code))

    def recogniseType(self, code):
        return self.recognise(code)[0]

    def recogniseCode(self, code):
        return self.recognise(code)[1]

    # 返回 {代码类型：代码列表}}
    def getMarketCode(self):
        res = {}
        for code in self.__codesInfo:
            value = self.__codesInfo[code][1]
            if res.get(value) == None:
                res[value] = []
            res[value].append(code)
        return res

    # 返回传入格式的代码
    def unRecognise(self, ustr):
        if self.__codesInfo.get(ustr):
            return self.__codesInfo[ustr][0]
        else:
            for key in self.__codesInfo:
                if ustr in key:
                    return self.__codesInfo[key][0]
        return ustr


# 时间参数格式化 - 返回datetime
class dateTimeFormator(object):
    SELF = None

    def __init__(self):
        self.timeReg = r'^(\d{4})([-/]?)(0[1-9]|1[012])\2(0[1-9]|[12][\d]|3[01])(?:\s+)([012]\d)(:?)([0-5]\d)\6([0-5]\d(?:\.\d*)?)$'
        self.dateReg = r'^(\d{4})([-/]?)(0[1-9]|1[012])\2(0[1-9]|[12][\d]|3[01])$'

    def format(self, date, delay=0, ms=False):
        if type(date) == datetime.datetime or type(date) == datetime.date:
            date = str(date)
        elif date == None:
            date = str(datetime.datetime.now())

        if type(date) in [str, unicode]:
            fstr = None
            if re.match(self.timeReg, date):
                temp = re.sub(self.timeReg, r'\1 \3 \4 \5 \7 \8', date).split()
                temp[5] = '%6.6f'%(float(temp[5]))
                if ms:
                    fstr = temp[:5] + temp[5].split('.')
                else:
                    fstr = temp[:5] + [temp[5].split('.')[0]]
            elif re.match(self.dateReg, date):
                fstr = re.sub(self.dateReg, r'\1 \3 \4 00 00 00', date).split()
            if fstr:
                flist = map(int, fstr)
                rtDate = datetime.datetime(*flist)
                if delay != 0:
                    rtDate += datetime.timedelta(days=delay)
                return rtDate
        raise Exception("time err:%s" % (str(date)))

instances = {}
def singleton(cls, *args, **kw):
    global instances
    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


def getDateFormator():
    if not dateTimeFormator.SELF:
        dateTimeFormator.SELF = dateTimeFormator()
    return dateTimeFormator.SELF


def dateFormat(*args, **kwargs):
    return getDateFormator().format(*args, **kwargs)


def getCodeRecognizer(codes):
    return codeRecognizer(codes)


def getList(code, fg=','):
    if type(code) in (str, unicode):
        return code.split(fg)
    elif type(code) == list:
        return code
    else:
        raise Exception('code type err %s:%s' % (str(type(code)), str(code)))


def getStr(fields, fg=','):
    if type(fields) == str:
        return fields
    elif type(fields) == list:
        return fg.join(fields)
    else:
        raise Exception('fields type err %s:%s' % (str(type(fields)), str(fields)))

def isSHFE(instrument):
    reg = r'^([a-zA-Z]+)\d+$'
    if re.sub(reg, r'\1', str(instrument)).upper() in SHFE_UNDERLYINGASSETS:
        return True
    else:
        return False

SHFE_UNDERLYINGASSETS = {'AG', 'AL', 'AU', 'BU', 'CU', 'FU', 'HC', 'NI', 'PB', 'RB', 'RU', 'SN', 'WR', 'ZN'}


IDXLIST = [
    u'H30263.SH', u'399401.SZ', u'399400.SZ', u'399403.SZ', u'399402.SZ',
    u'399405.SZ', u'399404.SZ', u'000152.SH', u'399406.SZ', u'000095.SH',
    u'000094.SH', u'000097.SH', u'000096.SH', u'000158.SH', u'000159.SH',
    u'000093.SH', u'000092.SH', u'000825.SH', u'000834.SH', u'399678.SZ',
    u'399647.SZ', u'000822.SH', u'CN6007.SZ', u'CN6006.SZ', u'CN6005.SZ',
    'CN6004.SZ', u'CN6003.SZ', u'CN6002.SZ', u'CN6001.SZ', u'399812.SZ',
    u'CN6009.SZ', u'CN6008.SZ', u'399810.SZ', u'399811.SZ', u'000020.SH',
    u'000021.SH', u'399120.SZ', u'399248.SZ', u'000025.SH', u'000026.SH',
    u'000155.SH', u'000028.SH', u'000029.SH', u'399241.SZ', u'000959.SH',
    u'399244.SZ', u'399707.SZ', u'000106.SH', u'000099.SH', u'000821.SH',
    u'000098.SH', u'000132.SH', u'399356.SZ', u'000929.SH', u'399407.SZ',
    u'H11077.SH', u'000919.SH', u'000925.SH', u'000924.SH', u'000927.SH',
    u'000153.SH', u'950093.SH', u'000920.SH', u'950091.SH', u'000922.SH',
    u'000956.SH', u'399409.SZ', u'000128.SH', u'399320.SZ', u'399408.SZ',
    u'000100.SH', u'CN5073.SZ', u'H50059.SH', u'399335.SZ', u'CN5077.SZ',
    u'CN5076.SZ', u'CN5075.SZ', u'399330.SZ', u'H50050.SH', u'000091.SH',
    u'CN5079.SZ', u'CN5078.SZ', u'H50054.SH', u'H50055.SH', u'399339.SZ',
    u'H50057.SH', u'399629.SZ', u'399628.SZ', u'000904.SH', u'399238.SZ',
    u'399299.SZ', u'399236.SZ', u'399620.SZ', u'399623.SZ', u'399622.SZ',
    '399625.SZ', u'399233.SZ', u'399230.SZ', u'399673.SZ', u'399551.SZ',
    u'399905.SZ', u'399906.SZ', u'399907.SZ', u'CN2341.SZ', u'399902.SZ',
    '399903.SZ', u'CN5107.SZ', u'H50058.SH', u'399908.SZ', u'399909.SZ',
    u'000990.SH', u'000991.SH', u'000992.SH', u'000993.SH', u'000994.SH',
    u'000995.SH', u'000996.SH', u'000997.SH', u'000998.SH', u'000999.SH',
    u'000917.SH', u'000148.SH', u'CN5106.SZ', u'399996.SZ', u'000842.SH',
    u'000843.SH', u'000840.SH', u'000841.SH', u'000846.SH', u'399995.SZ',
    u'000844.SH', u'399107.SZ', u'399994.SZ', u'CN5105.SZ', u'399640.SZ',
    u'399989.SZ', u'H00140.SH', u'399646.SZ', u'H30031.SH', u'000928.SH',
    u'H30034.SH', u'H30035.SH', u'399318.SZ', u'CN5103.SZ', u'CN6049.SZ',
    u'CN6048.SZ', u'399649.SZ', u'CNB201.SZ', u'CN6042.SZ', u'CN6041.SZ',
    'CNB202.SZ', u'CN6047.SZ', u'CN6046.SZ', u'CN6045.SZ', u'CN6044.SZ',
    u'000064.SH', u'000954.SH', u'000066.SH', u'000067.SH', u'000060.SH',
    u'000061.SH', u'000062.SH', u'000063.SH', u'399610.SZ', u'000068.SH',
    u'000069.SH', u'399975.SZ', u'399316.SZ', u'CN5088.SZ', u'000109.SH',
    u'000108.SH', u'000107.SH', u'399311.SZ', u'000105.SH', u'000104.SH',
    u'000103.SH', u'000102.SH', u'000101.SH', u'399310.SZ', u'CNB102.SZ',
    u'CNB103.SZ', u'CNB101.SZ', u'000952.SH', u'000953.SH', u'399348.SZ',
    u'399618.SZ', u'399972.SZ', u'CN2337.SZ', u'399619.SZ', u'H50014.SH',
    u'H50018.SH', u'H50019.SH', u'CN6039.SZ', u'CN6036.SZ', u'H50015.SH',
    u'CN6034.SZ', u'H50017.SH', u'CN6032.SZ', u'H50011.SH', u'H50012.SH',
    u'H50013.SH', u'399379.SZ', u'399378.SZ', u'399805.SZ', u'H50010.SH',
    u'399371.SZ', u'399370.SZ', u'399377.SZ', u'399376.SZ', u'399375.SZ',
    u'399374.SZ', u'CN6030.SZ', u'CN6031.SZ', u'399170.SZ', u'399395.SZ',
    u'399394.SZ', u'399397.SZ', u'399396.SZ', u'399391.SZ', u'000818.SH',
    u'399393.SZ', u'399392.SZ', u'000815.SH', u'000814.SH', u'000817.SH',
    u'000816.SH', u'000811.SH', u'399398.SZ', u'000813.SH', u'000812.SH',
    u'399399.SZ', u'CNB002.SZ', u'H40044.SH', u'H40043.SH', u'399321.SZ',
    u'399650.SZ', u'399373.SZ', u'000963.SH', u'399653.SZ', u'399654.SZ',
    u'399655.SZ', u'000967.SH', u'000966.SH', u'399306.SZ', u'399659.SZ',
    u'399305.SZ', u'399302.SZ', u'399303.SZ', u'399300.SZ', u'399301.SZ',
    u'000941.SH', u'399631.SZ', u'399959.SZ', u'399958.SZ', u'399957.SZ',
    u'399956.SZ', u'399955.SZ', u'399954.SZ', u'399953.SZ', u'399952.SZ',
    u'399951.SZ', u'399950.SZ', u'399240.SZ', u'H11098.SH', u'H11095.SH',
    u'000300.SH', u'399005.SZ', u'399004.SZ', u'399007.SZ', u'399006.SZ',
    u'399001.SZ', u'399003.SZ', u'399002.SZ', u'CNYX.SZ', u'399009.SZ',
    u'399008.SZ', u'399324.SZ', u'000131.SH', u'399249.SZ', u'000142.SH',
    u'000141.SH', u'000023.SH', u'000147.SH', u'399439.SZ', u'000145.SH',
    u'399434.SZ', u'399435.SZ', u'000149.SH', u'399437.SZ', u'399803.SZ',
    u'399431.SZ', u'399432.SZ', u'399433.SZ', u'399644.SZ', u'000027.SH',
    u'399243.SZ', u'399242.SZ', u'399802.SZ', u'950089.SH', u'399326.SZ',
    u'CN6072.SZ', u'CN6070.SZ', u'CN6071.SZ', u'000907.SH', u'000819.SH',
    u'000944.SH', u'399390.SZ', u'000136.SH', u'000137.SH', u'000134.SH',
    u'000135.SH', u'399135.SZ', u'399134.SZ', u'000130.SH', u'000038.SH',
    u'399139.SZ', u'000036.SH', u'000035.SH', u'000034.SH', u'000033.SH',
    u'000032.SH', u'000138.SH', u'000139.SH', u'399961.SZ', u'CN2339.SZ',
    u'000918.SH', u'000110.SH', u'399344.SZ', u'399440.SZ', u'000058.SH',
    u'399621.SZ', u'000911.SH', u'000912.SH', u'000913.SH', u'000914.SH',
    u'000915.SH', u'000916.SH', u'000810.SH', u'H50047.SH', u'H50046.SH',
    u'H50045.SH', u'H50044.SH', u'H50043.SH', u'H50042.SH', u'H50040.SH',
    u'H50049.SH', u'H50048.SH', u'399614.SZ', u'399615.SZ', u'399616.SZ',
    u'399341.SZ', u'399346.SZ', u'399611.SZ', u'399612.SZ', u'399613.SZ',
    u'CN5086.SZ', u'CN5087.SZ', u'CN5084.SZ', u'CN5085.SZ', u'CN5082.SZ',
    u'CN5083.SZ', u'CN5080.SZ', u'CN5081.SZ', u'000118.SH', u'399180.SZ',
    u'000119.SH', u'399637.SZ', u'000151.SH', u'399220.SZ', u'399913.SZ',
    u'399912.SZ', u'399911.SZ', u'399910.SZ', u'399917.SZ',
    u'399916.SZ', u'399915.SZ', u'399914.SZ', u'000903.SH',
    u'399919.SZ', u'399918.SZ', u'000039.SH', u'000975.SH',
    u'000989.SH', u'000988.SH', u'000987.SH', u'000986.SH', u'000985.SH',
    u'000984.SH', u'H01077.SH', u'000982.SH', u'000981.SH', u'000980.SH',
    u'399550.SZ', u'000851.SH', u'000850.SH', u'000853.SH', u'000852.SH',
    u'000855.SH', u'000854.SH', u'000857.SH', u'000856.SH', u'399984.SZ',
    u'399985.SZ', u'399986.SZ', u'399987.SZ', u'399980.SZ',
    u'399981.SZ', u'399982.SZ', u'399983.SZ', u'000926.SH', u'000901.SH',
    u'000921.SH', u'950092.SH', u'399966.SZ', u'399967.SZ', u'CN2324.SZ',
    u'399965.SZ', u'399962.SZ', u'399963.SZ', u'399960.SZ', u'000858.SH',
    u'000964.SH', u'950090.SH', u'CN2328.SZ', u'399969.SZ', u'CN6118.SZ',
    u'000090.SH', u'399642.SZ', u'000073.SH', u'000072.SH', u'000071.SH',
    u'000070.SH', u'000077.SH', u'000076.SH', u'000075.SH', u'000074.SH',
    u'000008.SH', u'000079.SH', u'000078.SH', u'000961.SH', u'399651.SZ',
    u'399652.SZ', u'399617.SZ', u'000962.SH', u'000965.SH', u'CN6037.SZ',
    u'399319.SZ', u'399337.SZ', u'399656.SZ', u'399657.SZ', u'399602.SZ',
    u'399634.SZ', u'399658.SZ', u'H50009.SH', u'H50008.SH', u'CN6029.SZ',
    u'CN6028.SZ', u'399307.SZ', u'H50003.SH', u'CN6024.SZ', u'H50001.SH',
    u'CN6026.SZ', u'H50007.SH', u'CN6020.SZ', u'CN6023.SZ', u'CN6022.SZ',
    u'000006.SH', u'CN2326.SZ', u'000004.SH', u'000005.SH', u'000002.SH',
    u'H40079.SH', u'000001.SH', u'CN5074.SZ', u'399964.SZ', u'000923.SH',
    u'000009.SH', u'930767.SH', u'H50051.SH', u'399140.SZ', u'000031.SH',
    u'000828.SH', u'000829.SH', u'H50053.SH', u'000820.SH', u'399817.SZ',
    u'399814.SZ', u'000823.SH', u'000824.SH', u'399813.SZ', u'000826.SH',
    u'000827.SH', u'H50056.SH', u'000030.SH', u'000983.SH', u'399626.SZ',
    u'CN5110.SZ', u'CN5111.SZ', u'399369.SZ', u'000958.SH', u'399968.SZ',
    u'000808.SH', u'399648.SZ', u'399315.SZ', u'399314.SZ', u'399645.SZ', u'000957.SH', u'399643.SZ', u'000951.SH',
    u'399641.SZ',
    u'399312.SZ', u'H50006.SH', u'399239.SZ', u'H00160.SH', u'399928.SZ', u'399929.SZ', u'000955.SH', u'399237.SZ',
    u'399922.SZ', u'399923.SZ',
    u'399920.SZ', u'399921.SZ', u'399926.SZ', u'399927.SZ', u'399924.SZ', u'399925.SZ', u'399235.SZ', u'399436.SZ',
    u'399232.SZ', u'399298.SZ',
    u'399624.SZ', u'399364.SZ', u'399317.SZ', u'399627.SZ', u'950078.SH', u'399100.SZ', u'399231.SZ', u'CN6043.SZ',
    u'399904.SZ', u'H30086.SH',
    u'399313.SZ', u'399354.SZ', u'CN2346.SZ', u'399429.SZ', u'399428.SZ', u'399423.SZ', u'399420.SZ', u'399427.SZ',
    u'399901.SZ', u'000150.SH',
    u'000950.SH', u'399137.SZ', u'CNYR.SZ', u'H40082.SH', u'CN6060.SZ', u'H40080.SH', u'CN2348.SZ', u'399663.SZ',
    u'000125.SH', u'000048.SH', u'000049.SH', u'399108.SZ', u'000120.SH', u'000123.SH',
    u'000122.SH', u'000042.SH', u'000043.SH', u'000040.SH', u'000012.SH', u'000129.SH', u'399101.SZ', u'000044.SH',
    u'000045.SH', u'399608.SZ', u'399333.SZ', u'000022.SH', u'399706.SZ', u'000018.SH', u'H50032.SH', u'H50033.SH',
    u'H50030.SH', u'H50031.SH', u'H50036.SH', u'H50037.SH', u'H50034.SH', u'H50035.SH', u'CN6115.SZ', u'CN6114.SZ',
    u'CN6117.SZ', u'CN6116.SZ', u'CN6111.SZ', u'CN6113.SZ', u'CN6112.SZ', u'399351.SZ', u'399332.SZ', u'399353.SZ',
    u'399352.SZ', u'399355.SZ', u'CN5098.SZ', u'399357.SZ', u'399604.SZ', u'399359.SZ', u'399358.SZ', u'CN5097.SZ',
    u'399381.SZ', u'CN5091.SZ', u'CN5090.SZ', u'CN5093.SZ', u'CN5092.SZ', u'CN6027.SZ', u'399190.SZ', u'CN2008.SZ',
    u'399210.SZ', u'399234.SZ', u'000126.SH', u'000908.SH', u'000121.SH', u'000801.SH', u'CN2610.SZ', u'CN6021.SZ',
    u'399676.SZ', u'000906.SH', u'000905.SH', u'399998.SZ', u'399672.SZ', u'000902.SH', u'399670.SZ',
    u'399671.SZ', u'399993.SZ', u'399992.SZ', u'399991.SZ', u'399990.SZ', u'399997.SZ', u'399106.SZ', u'000909.SH',
    u'399679.SZ', u'000041.SH', u'000046.SH', u'000047.SH', u'CN2335.SZ', u'399974.SZ', u'399977.SZ', u'399976.SZ',
    u'399971.SZ', u'399970.SZ', u'399973.SZ', u'CN2332.SZ', u'399103.SZ', u'399979.SZ', u'399978.SZ', u'950085.SH',
    u'000938.SH', u'399668.SZ', u'000939.SH', u'950088.SH', u'399804.SZ', u'399368.SZ', u'399807.SZ', u'000847.SH',
    u'000935.SH', u'000845.SH', u'399412.SZ', u'399413.SZ', u'399410.SZ', u'399411.SZ', u'399416.SZ', u'399417.SZ',
    u'399415.SZ', u'399553.SZ', u'399552.SZ', u'399418.SZ', u'399419.SZ', u'399557.SZ', u'399556.SZ', u'399555.SZ',
    u'399554.SZ', u'000849.SH', u'000161.SH', u'000160.SH', u'000162.SH', u'000140.SH',
    u'399438.SZ', u'000146.SH', u'930620.SH', u'CN6018.SZ', u'CN6019.SZ', u'CN6010.SZ', u'CN6011.SZ', u'CN6012.SZ',
    u'CN6013.SZ', u'CN6014.SZ', u'CN6015.SZ', u'CN6016.SZ', u'CN6017.SZ', u'000015.SH', u'399665.SZ', u'000017.SH',
    u'000016.SH', u'000011.SH', u'000010.SH', u'000013.SH', u'000973.SH', u'000019.SH', u'399667.SZ', u'H30373.SH',
    u'399666.SZ', u'399372.SZ', u'399481.SZ', u'399661.SZ', u'000977.SH', u'950080.SH', u'950081.SH', u'950082.SH',
    u'399809.SZ', u'399808.SZ', u'950086.SH', u'950087.SH', u'000936.SH', u'000937.SH', u'000934.SH', u'399806.SZ',
    u'000932.SH', u'000933.SH', u'000930.SH', u'000931.SH', u'H50016.SH', u'H50068.SH', u'399701.SZ', u'H50069.SH',
    u'CN5061.SZ', u'CN5062.SZ', u'H50065.SH', u'H50064.SH', u'H50067.SH', u'H50066.SH', u'H50061.SH', u'H50060.SH',
    u'H50063.SH', u'H50062.SH', u'399328.SZ', u'399329.SZ', u'399638.SZ', u'399639.SZ', u'CN5108.SZ', u'399632.SZ',
    u'000942.SH', u'399630.SZ', u'000940.SH', u'000947.SH', u'CN5102.SZ', u'000945.SH',
    u'399635.SZ', u'CN5069.SZ', u'399939.SZ', u'399938.SZ', u'399200.SZ', u'399931.SZ', u'399930.SZ', u'399933.SZ',
    u'399932.SZ', u'399935.SZ', u'399934.SZ', u'399937.SZ', u'399936.SZ', u'H50039.SH', u'000969.SH', u'000949.SH',
    u'399677.SZ', u'000837.SH', u'000836.SH', u'000835.SH', u'000948.SH', u'000833.SH', u'000832.SH', u'000831.SH',
    u'000830.SH', u'000839.SH', u'000838.SH', u'000968.SH', u'399350.SZ', u'000052.SH', u'399674.SZ', u'000943.SH',
    u'399633.SZ', u'CN5099.SZ', u'399322.SZ', u'399606.SZ', u'CN5104.SZ', u'000055.SH', u'399636.SZ', u'399675.SZ',
    u'000946.SH', u'CN5095.SZ', u'399943.SZ', u'CN5101.SZ', u'CN5094.SZ', u'CNB003.SZ', u'000910.SH', u'CNB001.SZ',
    u'CN5100.SZ', u'CN5089.SZ', u'399102.SZ', u'CN5096.SZ', u'CN6058.SZ', u'CN6059.SZ', u'CN6054.SZ', u'CN6055.SZ',
    u'CN6056.SZ', u'CN6057.SZ', u'CN6050.SZ', u'CN6051.SZ', u'CN6052.SZ', u'CN6053.SZ', u'CN6025.SZ', u'399689.SZ',
    u'399688.SZ', u'H50002.SH', u'399683.SZ', u'399682.SZ', u'399681.SZ',
    u'399680.SZ', u'399687.SZ', u'399686.SZ', u'399685.SZ', u'399684.SZ', u'000059.SH', u'000111.SH', u'000112.SH',
    u'000113.SH', u'000114.SH', u'000115.SH', u'000116.SH', u'000117.SH', u'000051.SH', u'000050.SH', u'000053.SH',
    u'399110.SZ', u'399441.SZ', u'000054.SH', u'000057.SH', u'000056.SH', u'H50038.SH', u'H50005.SH', u'H50004.SH',
    u'000960.SH', u'000007.SH', u'H11108.SH', u'H50021.SH', u'H50020.SH', u'H50023.SH', u'H50022.SH', u'H50025.SH',
    u'H50024.SH', u'H50027.SH', u'H50026.SH', u'H50029.SH', u'H50028.SH', u'000003.SH', u'950071.SH', u'950070.SH',
    u'950073.SH', u'950072.SH', u'950075.SH', u'950074.SH', u'950077.SH', u'950076.SH', u'950079.SH', u'399365.SZ',
    u'399366.SZ', u'399367.SZ', u'399360.SZ', u'399361.SZ', u'399362.SZ', u'399363.SZ', u'399160.SZ', u'399386.SZ',
    u'399387.SZ', u'399384.SZ', u'399385.SZ', u'399382.SZ', u'399383.SZ', u'399380.SZ', u'000809.SH', u'000806.SH',
    u'000807.SH', u'000804.SH', u'000805.SH', u'000802.SH', u'000803.SH', u'399388.SZ',
    u'399389.SZ', u'CN2608.SZ', u'CN2604.SZ', u'CN2602.SZ', u'000972.SH', u'399664.SZ', u'000970.SH', u'000971.SH',
    u'000976.SH', u'399660.SZ', u'000974.SH', u'399662.SZ', u'399702.SZ', u'399703.SZ', u'000978.SH', u'000979.SH',
    u'399669.SZ', u'CNB203.SZ', u'399704.SZ', u'399705.SZ', u'399131.SZ', u'399130.SZ', u'399150.SZ', u'399011.SZ',
    u'399133.SZ', u'399940.SZ', u'399941.SZ', u'399942.SZ', u'399132.SZ', u'399944.SZ', u'399945.SZ', u'399946.SZ',
    u'399947.SZ', u'399948.SZ', u'399949.SZ', u'000133.SH', u'H11080.SH', u'H11081.SH', u'H11082.SH', u'H11083.SH',
    u'H11084.SH', u'H11085.SH', u'H11086.SH', u'000065.SH', u'399136.SZ', u'000037.SH', u'399015.SZ', u'399012.SZ',
    u'399013.SZ', u'399010.SZ', u'399138.SZ', u'CN6033.SZ', u'930768.SZ'
]