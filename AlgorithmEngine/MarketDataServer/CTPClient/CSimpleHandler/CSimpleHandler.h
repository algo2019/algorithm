#ifndef __CSIMPLE_HANDLER__
#define __CSIMPLE_HANDLER__

#include <stdio.h>
#include <iostream>
#include <stdlib.h>
#include <string.h>
#include "ThostFtdcMdApi.h"

using namespace std;

class IMsgProcessor
{
    public:
        virtual void process(CThostFtdcDepthMarketDataField *futureData) = 0;
};

class CSimpleHandler : public CThostFtdcMdSpi
{
    public:
        CSimpleHandler(string& brokerID, string& investorID, string& password, string& frontAddress);

        ~CSimpleHandler();

        void InitProcess(IMsgProcessor* processor);
        // 当客户端与交易托管系统建立起通信连接,客户端需要进行登录
        void OnFrontConnected() ;

        // 当客户端与交易托管系统通信连接断开时,该方法被调用
        void OnFrontDisconnected(int nReason);

        // 当客户端发出登录请求之后,该方法会被调用,通知客户端登录是否成功
        void OnRspUserLogin(CThostFtdcRspUserLoginField *pRspUserLogin, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

        void ReqInstrumentData(char** instruments, int len);

        void OnRspSubMarketData(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
        // 行情应答
        void OnRtnDepthMarketData(CThostFtdcDepthMarketDataField *futureData);

        // 针对用户请求的出错通知
        void OnRspError(CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

    private:
        CThostFtdcMdApi *m_pUserApi;
        string m_brokerID;
        string m_investorID;
        string m_password;
        IMsgProcessor* m_processor;
};

#endif
