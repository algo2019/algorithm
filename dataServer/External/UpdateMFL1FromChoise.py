def login_choise():
    from EmQuantAPI import *
    from datetime import timedelta, datetime

    def startCallback(message):
        print "[EmQuantAPI Python]", message
        return 1

    def demoQuoteCallback(quantdata):
        """
        DemoCallback 是EM_CSQ订阅时提供的回调函数模板。该函数只有一个为c.EmQuantData类型的参数quantdata
        :param quantdata:c.EmQuantData
        :return:
        """
        print "demoQuoteCallback,", str(quantdata)

    def cstCallBack(quantdata):
        """
        cstCallBack 是EM_CST订阅时提供的回调函数模板。该函数只有一个为c.EmQuantData类型的参数quantdata
        :param quantdata:c.EmQuantData
        :return:
        """
        for i in range(0, len(quantdata.Codes)):
            length = len(quantdata.Dates)
            for it in quantdata.Data.keys():
                print it
                for k in range(0, length):
                    for j in range(0, len(quantdata.Indicators)):
                        print quantdata.Data[it][j * length + k], " ",
                    print ""

    # 调用登录函数（激活后使用，不需要用户名密码）
    loginResult = c.start("ForceLogin=1")

    if (loginResult.ErrorCode != 0):
        print "login in fail"
        exit()
        
    return c

