// TraderSpi.cpp# implementation of the CTraderSpi class.
//
//////////////////////////////////////////////////////////////////////

//|include "StdAfx.h"
#include "TraderSpi.h"
#include "FinanceLogger.h"
#include <string.h>
#include <stdlib.h>
#include <iostream>
#include "PublicDefine.h"
#include "stdarg.h"
#include <string>
#include "time.h"
#include <stdio.h>

using namespace std;
volatile int lastQueryFinish = 0;

using namespace FinanceLogger;
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////
CTraderSpi::CTraderSpi()
{
	m_pUserApi = NULL;
	m_nRequestId = 0;
	m_bOpen = true;
	m_bLogedIn = false;
	onRtnTradeEvent = new Event();
	onRtnOrderEvent = new Event();
	m_OnRspQryTradingAccountHandler = NULL;
	m_OnRspQryInvestorPositionDetailHandler = NULL;
}

CTraderSpi::~CTraderSpi()
{
	if (m_pUserApi)
	{
		m_pUserApi->Release();
		m_pUserApi = NULL;
	}
	delete onRtnTradeEvent;
	delete onRtnOrderEvent;
}

void CTraderSpi::OnFrontConnected()
{
	ReqUserLogin();
}

void CTraderSpi::ReqUserLogin()
{
	CThostFtdcReqUserLoginField req;
	memset(&req, 0, sizeof(req));
	strcpy(req.BrokerID, m_brokerID);
	strcpy(req.UserID, m_userName);
	strcpy(req.Password, m_password);
	int iResult = m_pUserApi->ReqUserLogin(&req, ++m_nRequestId);
	if (iResult == 0)
	{
		FormatLog(LOG_APP_LEVEL, "ReqUserLogin", "OK");
	}
	else
	{
		FormatLog(LOG_ERROR_LEVEL, "ReqUserLogin", "ERR");
	}
}

void CTraderSpi::OnRspUserLogin( CThostFtdcRspUserLoginField *pRspUserLogin, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast )
{
	if (bIsLast && !IsErrorRspInfo(pRspInfo))
	{
		m_frontID = pRspUserLogin->FrontID;
		m_sessionID = pRspUserLogin->SessionID;
		int iNextOrderRef = atoi(pRspUserLogin->MaxOrderRef);
		iNextOrderRef++;
		sprintf(m_orderRef, "%d", iNextOrderRef);
		FormatLog(LOG_APP_LEVEL, "OnRspUserLogin", "User [%s] Login success m_orderRef # %s", pRspUserLogin->UserID, m_orderRef);
		m_bLogedIn = true;
		ReqSettlementInfoConfirm();
	}
	else
	{
		char strFormat[500];
		sprintf(strFormat, "User [%s] Login Failure ErrCode#%d, ErrMsg#%s", pRspUserLogin->UserID, pRspInfo->ErrorID, pRspInfo->ErrorMsg);
		FormatLog(LOG_ERROR_LEVEL, "OnRspUserLogin", strFormat);
	}
}

void CTraderSpi::OnRspSettlementInfoConfirm( CThostFtdcSettlementInfoConfirmField *pSettlementInfoConfirm, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast )
{
    if (pRspInfo && pRspInfo->ErrorID != 0)
    {
        FormatLog(LOG_ERROR_LEVEL, "OnRspSettlementInfoConfirm", pRspInfo->ErrorMsg);
        return;
    }
    FormatLog(LOG_APP_LEVEL, "OnRspSettlementInfoConfirm", "ready");
}

void CTraderSpi::OnRspQryInstrument( CThostFtdcInstrumentField *pInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast )
{
	
}

void CTraderSpi::SetOnRspQryTradingAccountHandler(on_rtn_trading_account_ptr handler){
	m_OnRspQryTradingAccountHandler = handler;
}

void CTraderSpi::SetOnRspQryInvestorPositionDetailHandler(on_rtn_position_detail_ptr handler){
	m_OnRspQryInvestorPositionDetailHandler = handler;
}

void CTraderSpi::OnRspQryTradingAccount(CThostFtdcTradingAccountField *pTradingAccount, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	if (m_OnRspQryTradingAccountHandler == NULL){
        FormatLog(LOG_APP_LEVEL, "OnRspQryTradingAccount", "handler is NULL");
		return;
	}
	else{
		(*m_OnRspQryTradingAccountHandler)(pTradingAccount, pRspInfo, nRequestID, bIsLast);
        FormatLog(LOG_APP_LEVEL, "OnRspQryTradingAccount", "send one tip");
	}
}

void CTraderSpi::OnRspQryInvestorPosition( CThostFtdcInvestorPositionField *pInvestorPosition, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast )
{
	
}

std::string CTraderSpi::ReqOrderInsert(char* chInstrment, double price, char offsetFlag, char direction, int volumn, char orderPriceType, 
                            char timeCondition, char contingentCondition, int local_ref)
{
	CThostFtdcInputOrderField req;
	memset(&req, 0, sizeof(req));
	strcpy(req.BrokerID, m_brokerID);
	strcpy(req.InvestorID, m_userName);
	strcpy(req.InstrumentID, chInstrment);
	strcpy(req.OrderRef, m_orderRef);
    req.TimeCondition = timeCondition;
    req.ContingentCondition = contingentCondition;
	req.OrderPriceType = orderPriceType;
	req.Direction = direction;
	req.CombOffsetFlag[0] = offsetFlag;
	req.CombHedgeFlag[0] = THOST_FTDC_HF_Speculation;
	req.LimitPrice = price;
	req.VolumeTotalOriginal = volumn;
	req.VolumeCondition = THOST_FTDC_VC_AV;
	req.MinVolume = 1;
	req.ContingentCondition = THOST_FTDC_CC_Immediately;
	req.ForceCloseReason = THOST_FTDC_FCC_NotForceClose;
	req.IsAutoSuspend = 0;
	req.UserForceClose = 0;
    req.RequestID = m_nRequestId;
    int iNextOrderRef = atoi(m_orderRef);
    orderRefNameMap[iNextOrderRef] = local_ref;
    nameOrderRefMap[local_ref] = iNextOrderRef;
	m_pUserApi->ReqOrderInsert(&req, m_nRequestId);
	iNextOrderRef++;
	sprintf(m_orderRef, "%d", iNextOrderRef);

    FormatLog(LOG_APP_LEVEL, "ReqOrderInsert", "localRef # %d m_orderRef # %s", local_ref, m_orderRef);
    FormatLog(LOG_APP_LEVEL, "ReqOrderInsert", "m_nRequestId # %d", ++m_nRequestId);
	FormatLog(LOG_APP_LEVEL, "ReqOrderInsert", "User#[%s] insert [%s][%s] [Price#%.2lf][Amount#%d]", m_userName, chInstrment, direction=='0'? "buy":"self", price, volumn);
    return m_orderRef;
}

void CTraderSpi::OnRspOrderInsert( CThostFtdcInputOrderField *pInputOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast )
{
	if (IsErrorRspInfo(pRspInfo))
	{
		CThostFtdcOrderField pOrder;
		memset(&pOrder, 0, sizeof(CThostFtdcOrderField));
		sprintf(pOrder.OrderRef, "%d", orderRefNameMap[atoi(pInputOrder->OrderRef)]);
		sprintf(pOrder.InstrumentID, "%s", pInputOrder->InstrumentID);
		pOrder.OrderStatus = '6';
		pOrder.VolumeTraded = 0;
		pOrder.VolumeTotal = pInputOrder->VolumeTotalOriginal;
		sprintf(pOrder.StatusMsg, "%s", pRspInfo->ErrorMsg);
		OnRtnOrder(&pOrder);
		char strTmp[500];
		sprintf(strTmp, "Error response errCode#%d, errMsg#%s", pRspInfo->ErrorID, pRspInfo->ErrorMsg);
		FormatLog(LOG_ERROR_LEVEL, "OnRspOrderInsert", strTmp);
	}
	else
	{
		FormatLog(LOG_APP_LEVEL, "OnRspOrderInsert", "Sucess");	
	}

}

void CTraderSpi::ReqOrderAction(const std::string& InstrumentID, int localRef, const int8_t ActionFlag)
{
    char orderRef[10];
    sprintf(orderRef, "%d", nameOrderRefMap[localRef]);
    CThostFtdcInputOrderActionField action;
    memset(&action, 0, sizeof(action));

    strncpy(action.InstrumentID, InstrumentID.c_str(), InstrumentID.length());
    strcpy(action.BrokerID, m_brokerID);
    strcpy(action.InvestorID, m_userName);

    action.SessionID = m_sessionID;
    action.FrontID = m_frontID;
    strncpy(action.OrderRef, orderRef, sizeof(orderRef));
    action.ActionFlag = ActionFlag;

    FormatLog(LOG_APP_LEVEL, "ReqOrderAction", "localRef # %d | m_nRequestId # %d", localRef, m_nRequestId);
}

void CTraderSpi::OnRspOrderAction( CThostFtdcInputOrderActionField *pInputOrderAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast )
{
	if (pRspInfo && pRspInfo->ErrorID != 0)
	{
		char strFormat[500];
		sprintf(strFormat, "OrderAction Failed#[%d-%s]", pRspInfo->ErrorID, pRspInfo->ErrorMsg);
		FormatLog(LOG_ERROR_LEVEL, "OnRspOrderAction", strFormat);
	}
	else
	{
    FormatLog(LOG_APP_LEVEL, "OnRsqOrderAction", "ActionFlag %c", pInputOrderAction->ActionFlag);
    FormatLog(LOG_APP_LEVEL, "OnRspOrderAction", "Rsp success");
	}
}

void CTraderSpi::OnRspError( CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast )
{
	
}

void CTraderSpi::OnFrontDisconnected( int nReason )
{
	char strTmp[500];
	sprintf(strTmp, "Reason# %d", nReason);
	FormatLog(LOG_WARN_LEVEL, "OnFrontDisconnected", strTmp);
}

void CTraderSpi::OnHeartBeatWarning( int nTimeLapse )
{
	
}

void CTraderSpi::OnRtnOrder(CThostFtdcOrderField *pOrder)
{
	FormatLog(LOG_APP_LEVEL, "OnRtnOrder", "Rtn order emit");
	sprintf(pOrder->OrderRef, "%d", orderRefNameMap[atoi(pOrder->OrderRef)]);
	char msg[1024];
	sprintf(msg,"OrderRef#%s|InstrumentID#%s|OrderStatus#%c|VolumeTraded#%d|VolumeTotal#%d|InsertTime#%s|ActiveTime#%s|SuspendTime#%s|UpdateTime#%s|CancelTime#%s",
		pOrder->OrderRef, pOrder->InstrumentID, pOrder->OrderStatus,pOrder->VolumeTraded, pOrder->VolumeTotal, pOrder->InsertTime, pOrder->ActiveTime, pOrder->SuspendTime, pOrder->UpdateTime, pOrder->CancelTime);
    FormatLog(LOG_APP_LEVEL, "OnRspOderAction", msg);
	onRtnOrderEvent->emit((void *) pOrder);
	FormatLog(LOG_APP_LEVEL, "OnRtnOrder", "Rtn order over");
}

void CTraderSpi::OnRtnTrade( CThostFtdcTradeField *pTrade )
{
	FormatLog(LOG_APP_LEVEL, "OnRtnTrade", "Rtn trade emit");
	sprintf(pTrade->OrderRef, "%d", orderRefNameMap[atoi(pTrade->OrderRef)]);
	char msg[1024];
	sprintf(msg, "InstrumentID#%s|OrderRef#%s|Direction#%c|OffsetFlag#%c|Price#%f|Volume#%d|TradingDay#%s|TradeID#%s",
		pTrade->InstrumentID ,pTrade->OrderRef ,pTrade->Direction ,pTrade->OffsetFlag ,pTrade->Price ,pTrade->Volume ,pTrade->TradingDay ,pTrade->TradeID);
	FormatLog(LOG_APP_LEVEL, "OnRtnTrade", msg);
	onRtnTradeEvent->emit((void *) pTrade);
	FormatLog(LOG_APP_LEVEL, "OnRtnTrade", "Rtn trade leave");
}

void CTraderSpi::ReqSettlementInfoConfirm()
{
	FormatLog(LOG_APP_LEVEL, "ReqSettlementInfoConfirm", "start");
	CThostFtdcSettlementInfoConfirmField pSettlementInfoConfirm;
	strcpy(pSettlementInfoConfirm.BrokerID, m_brokerID);
	strcpy(pSettlementInfoConfirm.InvestorID, m_userName);
	m_pUserApi->ReqSettlementInfoConfirm(&pSettlementInfoConfirm, ++m_nRequestId);
}

void CTraderSpi::ReqQryInstrument()
{
	
}

int CTraderSpi::ReqQryTradingAccount(CThostFtdcQryTradingAccountField *pQryInvestorPositionDetail)
{
  m_pUserApi->ReqQryTradingAccount(pQryInvestorPositionDetail, ++m_nRequestId);
  return m_nRequestId;
}

void CTraderSpi::ReqQryInvestorPosition()
{
	
}

bool CTraderSpi::IsErrorRspInfo( CThostFtdcRspInfoField *pRspInfo )
{
	return ((pRspInfo) && (pRspInfo->ErrorID != 0));
}

bool CTraderSpi::IsMyOrder( CThostFtdcOrderField *pOrder )
{
	return ((pOrder->FrontID == m_frontID) &&
		(pOrder->SessionID == m_sessionID) &&
			(strcmp(pOrder->OrderRef, m_orderRef) == 0));
}

bool CTraderSpi::IsTradingOrder( CThostFtdcOrderField *pOrder )
{
	return ((pOrder->OrderStatus != THOST_FTDC_OST_PartTradedNotQueueing) &&
		(pOrder->OrderStatus != THOST_FTDC_OST_Canceled) &&
			(pOrder->OrderStatus != THOST_FTDC_OST_AllTraded));
}

void CTraderSpi::FormatLog( int nLevel, const char* strDomain, const char* szFormat, ...)
{
	char strLog[1000],szParam[500];
	va_list args;
	va_start(args,szFormat);
	vsnprintf(szParam, 490, szFormat, args);
	va_end(args);
	sprintf(strLog, "%s %s", strDomain, szParam);
  switch(nLevel)
  {
  case LOG_APP_LEVEL:
    FINANCE_INFO(strLog);
    break;
  case LOG_DEBUG_LEVEL:
    FINANCE_DEBUG(strLog);
    break;
  case LOG_WARN_LEVEL:
    FINANCE_WARN(strLog);
    break;
  case LOG_ERROR_LEVEL:
    FINANCE_ERROR(strLog);
    break;
  }
}

void CTraderSpi::Init(char* szAddress, char* redisAddress, int redisPort, char* publishKey)
{
	if (m_pUserApi == NULL)
	{
		FormatLog(LOG_APP_LEVEL, "Init", "m_pUserApi->RegisterSpi");
        m_pUserApi = CThostFtdcTraderApi::CreateFtdcTraderApi();
		m_pUserApi->RegisterSpi(this);
		m_pUserApi->RegisterFront(szAddress);
		m_pUserApi->Init();
        m_redisAddress = redisAddress;
        m_redisPort = redisPort;
        m_publishKey = publishKey;
	}
}

int CTraderSpi::ReqQryInvestorPositionDetail(CThostFtdcQryInvestorPositionDetailField *pQryInvestorPositionDetail)
{
    m_pUserApi->ReqQryInvestorPositionDetail(pQryInvestorPositionDetail, ++m_nRequestId);
    return m_nRequestId;
}

void CTraderSpi::OnRspQryInvestorPositionDetail(CThostFtdcInvestorPositionDetailField *pInvestorPositionDetail, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	if (m_OnRspQryInvestorPositionDetailHandler == NULL){
        FormatLog(LOG_APP_LEVEL, "OnRspQryTradingAccount", "handler is NULL");
		return;
	}
	else{
		(*m_OnRspQryInvestorPositionDetailHandler)(pInvestorPositionDetail, pRspInfo, nRequestID, bIsLast);
    	FormatLog(LOG_APP_LEVEL, "OnRspQryInvestorPositionDetail", "send on tick");
	}
}

void CTraderSpi::ReqQryOrder( CThostFtdcQryOrderField *pQryOrder)
{
	int iResult = m_pUserApi->ReqQryOrder(pQryOrder, ++m_nRequestId);
	if (iResult != 0)
	{
		FormatLog(LOG_WARN_LEVEL, "ReqQryOrder", "...ERR...");
	}
}

void CTraderSpi::OnRspQryOrder( CThostFtdcOrderField *pOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast )
{
	if (pRspInfo && pRspInfo != 0)
	{
		char szBuf[500];
		sprintf(szBuf, "ErrorID#%d, ErrMsg#%s", pRspInfo->ErrorID, pRspInfo->ErrorMsg);
		FormatLog(LOG_ERROR_LEVEL, "OnRspQryOrder", szBuf);
	}
	else
	{
	    if (pOrder == NULL){
	    	FormatLog(LOG_ERROR_LEVEL, "OnRspQryOrder", "Error for pOrder is Null");
	    }
	    else{
    		OnRtnOrder(pOrder);
	    }
	}
}

void CTraderSpi::ReqQryTrade(CThostFtdcQryTradeField *pQryTrade)
{
    int iResult = m_pUserApi->ReqQryTrade(pQryTrade, ++m_nRequestId);
	if (iResult != 0)
	{
		FormatLog(LOG_WARN_LEVEL, "ReqQryTrade", "...ERR...");
	}
}

void CTraderSpi::OnRspQryTrade(CThostFtdcTradeField *pTrade, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
    if (pRspInfo && pRspInfo != 0)
	{
		char szBuf[500];
		sprintf(szBuf, "ErrorID#%d, ErrMsg#%s", pRspInfo->ErrorID, pRspInfo->ErrorMsg);
		FormatLog(LOG_ERROR_LEVEL, "ReqQryTrade", szBuf);
	}
	else
	{
	    if (pTrade == NULL){
	    	FormatLog(LOG_ERROR_LEVEL, "OnRspQryTrade", "Error for pQryTrade is Null");
	    }
	    else{
    		OnRtnTrade(pTrade);
	    }
    }
}


void CTraderSpi::SetUserInfo( const char* chUserName, const char* chPsw, const char* chBrokerID)
{
	strcpy(m_userName, chUserName);
	strcpy(m_password, chPsw);
	strcpy(m_brokerID, chBrokerID);
}


void CTraderSpi::SubscribeOnRtnOrder(handler_ptr handler)
{
	onRtnOrderEvent->subscribe(handler);
}

void CTraderSpi::SubscribeOnRtnTrade(handler_ptr handler)
{
	onRtnTradeEvent->subscribe(handler);
}
