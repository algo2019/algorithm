#include "InstrumnetGainer.h"

InstrumnetGainer::InstrumnetGainer(string& szAddress, string& brokerID, string& investorID, string& password) : m_brokerID(brokerID), m_investorID(investorID), m_password(password)
{
    loginState = false;
    m_pUserApi = CThostFtdcTraderApi::CreateFtdcTraderApi();
    m_pUserApi->RegisterSpi(this);
    m_pUserApi->RegisterFront(const_cast<char*>(szAddress.c_str()));
    m_pUserApi->Init();
    m_nRequestId = 0;
    end = 0;
    index = 0;
}

InstrumnetGainer::~InstrumnetGainer()
{
    if (m_pUserApi)
    {
        m_pUserApi->Release();
        m_pUserApi = NULL;
    }
}

void InstrumnetGainer::OnFrontConnected()
{
    ReqUserLogin();
}

void InstrumnetGainer::ReqUserLogin()
{
    CThostFtdcReqUserLoginField req;
    memset(&req, 0, sizeof(req));
    strcpy(req.BrokerID, m_brokerID.c_str());
    strcpy(req.UserID, m_investorID.c_str());
    strcpy(req.Password, m_password.c_str());
    int iResult = m_pUserApi->ReqUserLogin(&req, ++m_nRequestId);
    printf("req log in %d\n", iResult);
}

void InstrumnetGainer::OnRspUserLogin( CThostFtdcRspUserLoginField *pRspUserLogin, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast )
{
    if (bIsLast && pRspInfo->ErrorID == 0)
    {
        int iNextOrderRef = atoi(pRspUserLogin->MaxOrderRef);
        iNextOrderRef++;
        printf("login ok\n");
        loginState = true;
    }
    else{
        printf("login failed\n");
    }
}

bool InstrumnetGainer::IsLogin()
{
  return loginState;
}


void InstrumnetGainer::OnRspQryInstrument(CThostFtdcInstrumentField *pInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast )
{
    if(pInstrument){
        m_instruments[index] = new char[20];
        if (strlen(pInstrument->InstrumentID) < 8){
            sprintf(m_instruments[index], "%s", pInstrument->InstrumentID);
            index++;
        }
        if (bIsLast){
          end++;
        }
    }else{
        printf("pInstrument is Null!\n");
        exit(0);
    }
}

char** InstrumnetGainer::GetRes(){
  return m_instruments;
}

void InstrumnetGainer::ReqAllInstrument()
{
    index = 0;
    end = 0;
    CThostFtdcQryInstrumentField pQryInstrument = {0};
    printf("ReqAllInstrument\n");
    int iResult = m_pUserApi->ReqQryInstrument(&pQryInstrument, ++m_nRequestId);
    printf("ReqAllInstrumen Result %d\n", iResult);
}

bool InstrumnetGainer::IsEnd(){
  if(end == 1){
    return true;
  }
  return false;
}

int InstrumnetGainer::Len(){
  return index;
}
