#ifndef __INSTRUMENTS_GAINER__
#define __INSTRUMENTS_GAINER__

#include <stdio.h>
#include "ThostFtdcTraderApi.h"
#include <iostream>
#include <stdlib.h>
#include <string.h>

using namespace std;


class InstrumnetGainer : public CThostFtdcTraderSpi
{
  public:
        InstrumnetGainer(string& szAddress, string& brokerID, string& investorID, string& password);

        ~InstrumnetGainer();

        void OnFrontConnected();

        void ReqUserLogin();

        void OnRspUserLogin(CThostFtdcRspUserLoginField *pRspUserLogin, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast );

        void OnRspQryInstrument(CThostFtdcInstrumentField *pInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast );

        char** GetRes();

        void ReqAllInstrument();

        bool IsEnd();

        int Len();
        
        bool IsLogin();
    private:
        string m_password;
        string m_brokerID;
        string m_investorID;
        bool loginState;
        CThostFtdcTraderApi* m_pUserApi;
        int m_nRequestId;
        char* m_instruments[1000];
        int index;
        int end;
};

#endif
