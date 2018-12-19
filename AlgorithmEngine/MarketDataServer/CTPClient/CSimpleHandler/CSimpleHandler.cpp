#include "CSimpleHandler.h"
#include <sys/timeb.h>
#include <stdio.h>


double time()
{
  struct timespec t;
  clock_gettime(CLOCK_REALTIME, &t);
  return t.tv_sec + t.tv_nsec*0.000000001;
}

CSimpleHandler::CSimpleHandler(string& brokerID, string& investorID, string& password, string& frontAddress): m_brokerID(brokerID), m_investorID(investorID), m_password(password)
{
  m_pUserApi = CThostFtdcMdApi::CreateFtdcMdApi();
  m_pUserApi->RegisterSpi(this);
  m_pUserApi->RegisterFront(const_cast<char*>(frontAddress.c_str()));
  m_pUserApi->Init();
}

CSimpleHandler::~CSimpleHandler() {}

// 当客户端与交易托管系统建立起通信连接,客户端需要进行登录
void CSimpleHandler::OnFrontConnected() {
    CThostFtdcReqUserLoginField reqUserLogin;
    // get BrokerID
    printf("BrokerID:%s\n", m_brokerID.c_str());
    strcpy(reqUserLogin.BrokerID, m_brokerID.c_str());
    // get userid
    printf("userid:%s\n", m_investorID.c_str());
    strcpy(reqUserLogin.UserID, m_investorID.c_str());
    // get userid
    strcpy(reqUserLogin.Password, m_password.c_str());
    // 发出登陆请求
    m_pUserApi->ReqUserLogin(&reqUserLogin, 0);
}

// 当客户端与交易托管系统通信连接断开时,该方法被调用
void CSimpleHandler::OnFrontDisconnected(int nReason) {
    // 当发生这个情况后,API会自动重新连接,客户端可不做处理
    printf("OnFrontDisconnected.\n");
}

// 当客户端发出登录请求之后,该方法会被调用,通知客户端登录是否成功
void CSimpleHandler::OnRspUserLogin(CThostFtdcRspUserLoginField *pRspUserLogin, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
    printf("OnRspUserLogin:\n");
    printf("ErrorCode=[%d], ErrorMsg=[%s]\n", pRspInfo->ErrorID, pRspInfo->ErrorMsg);
    printf("RequestID=[%d], Chain=[%d]\n", nRequestID, bIsLast);
    if (pRspInfo->ErrorID != 0) {
        // 端登失败,客户端需进行错误处理
        printf("Failed to login, errorcode=%d errormsg=%s requestid=%d chain=%d", pRspInfo->ErrorID, pRspInfo->ErrorMsg, nRequestID, bIsLast);
        exit(-1);
    }
}

void CSimpleHandler::ReqInstrumentData(char* instruments[], int len)
{
    printf("ReqInstrumentData %d \n", len);
    int result = m_pUserApi->SubscribeMarketData(instruments, len);
    if (result == 0) {
        printf("ReqInstrumentData Success\n");
    } else {
        printf("ReqInstrumentData Failed: %d\n", result);
    };
}

void CSimpleHandler::InitProcess(IMsgProcessor* processor){
    m_processor = processor;
}

void CSimpleHandler::OnRspSubMarketData(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) {
    if(pRspInfo->ErrorID!=0) {
        printf("OnRspSubMarketData:\n");
        printf("ErrorCode=[%d], ErrorMsg=[%s]\n", pRspInfo->ErrorID, pRspInfo->ErrorMsg);
        printf("RequestID=[%d], Chain=[%d]\n", nRequestID, bIsLast); // 客户端需进行错误处理
    }
}

// 行情应答
void CSimpleHandler::OnRtnDepthMarketData(CThostFtdcDepthMarketDataField *futureData)
{
    m_processor->process(futureData);
}

// 针对用户请求的出错通知
void CSimpleHandler::OnRspError(CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast) {
    printf("OnRspError:\n");
    printf("ErrorCode=[%d], ErrorMsg=[%s]\n", pRspInfo->ErrorID, pRspInfo->ErrorMsg);
    printf("RequestID=[%d], Chain=[%d]\n", nRequestID, bIsLast); // 客户端需进行错误处理
    //{客户端的错误处理}
}
