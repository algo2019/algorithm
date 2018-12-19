#ifndef __CTP_TRADE_SERVICE__
#define __CTP_TRADE_SERVICE__


#include "PublicDefine.h"
#include "FinanceLogger.h"
#include "TraderSpi.h"
#include <iostream>
#include <fstream>
#include <cmath>
#include <hiredis/hiredis.h>
#include <string.h>


using namespace FinanceLogger;

using namespace std;

class TradeService{
	private:
		CTraderSpi* pTraderApi;
		string m_brokerID;
		string m_investorID;
		string m_password;
		string m_rohonFrontAddress;
		time_t last_time;
		char *m_redisAddress;
		int m_redisPort;
	public:
		TradeService(string& brokerID, string& investorID, string& password, string& rohonFrontAddress,
				string& redisAddress, int redisPort, string& publishKey):m_brokerID(brokerID), m_investorID(investorID),
				m_password(password) {
			char rohonLogFile[500] = "logs/RohonTradeEngine.log";
			FINANCE_INIT(rohonLogFile, "INFO");

			char tmpMsg[500];
			sprintf(tmpMsg, "RohonTraderHandler RohonTradeHander : %s %s %s", m_brokerID.c_str(), m_investorID.c_str(), m_password.c_str());
			FINANCE_INFO(tmpMsg);
			pTraderApi = new CTraderSpi();
			pTraderApi->SetUserInfo(m_investorID.c_str(), m_password.c_str(), m_brokerID.c_str());
			m_redisAddress = const_cast<char*>(redisAddress.c_str());
			m_redisPort = redisPort;
			pTraderApi->Init(const_cast<char*>(rohonFrontAddress.c_str()), m_redisAddress, m_redisPort, const_cast<char*>(publishKey.c_str()));
			last_time = time(NULL);
		}

		void ReqOrderInsert(string& chInstrument,double price, char offsetFlag, char direction, int volume, char orderPriceType, char timeCondition, char contingentCondition, int localRef){
			if (pTraderApi && pTraderApi->GetLoginStatus()) {
				FINANCE_INFO("ReqOrderInsert");
				pTraderApi->ReqOrderInsert(const_cast<char *>(chInstrument.data()), price, offsetFlag, direction, volume, orderPriceType, timeCondition, contingentCondition, localRef);
			}
			else{
				CThostFtdcOrderField pOrder;
				memset(&pOrder, 0, sizeof(CThostFtdcOrderField));
				sprintf(pOrder.OrderRef, "%d", localRef);
				sprintf(pOrder.InstrumentID, "%s", chInstrument.c_str());
				pOrder.OrderStatus = '6';
				pOrder.VolumeTraded = 0;
				pOrder.VolumeTotal = volume;
				sprintf(pOrder.StatusMsg, "用户未登录");
				pTraderApi->OnRtnOrder(&pOrder);
				FINANCE_INFO("ReqOrderInsert Err For Not Login");
			}
		}

		void ReqOrderAction( string& InstrumentID, int localRef, char ActionFlag) {
			if (pTraderApi && pTraderApi->GetLoginStatus()) {
				FINANCE_INFO("ReqOrderAction");
				pTraderApi->ReqOrderAction(InstrumentID, localRef, ActionFlag);
			}
			FINANCE_INFO("ReqOrderAction Err For Not Login");
		}

		int ReqQryInvestorPositionDetail( string& InstrumentID) {
			if (pTraderApi && pTraderApi->GetLoginStatus()) {
				FINANCE_INFO("ReqQryInverstorPositionDetail");
				CThostFtdcQryInvestorPositionDetailField position;
				strcpy(position.BrokerID, m_brokerID.c_str());
				strcpy(position.InvestorID, m_investorID.c_str());
				strcpy(position.InstrumentID, InstrumentID.c_str());
				return pTraderApi->ReqQryInvestorPositionDetail(&position);
			}else{
				FINANCE_INFO("ReqQryInverstorPositionDetail Err For Not Login");
				return -1;
			}
		}

		int ReqQryTradingAccount(){
			if (pTraderApi && pTraderApi->GetLoginStatus()) {
				CThostFtdcQryTradingAccountField account = {{0}};
				strcpy(account.BrokerID, m_brokerID.c_str());
				strcpy(account.InvestorID, m_investorID.c_str());
				return pTraderApi->ReqQryTradingAccount(&account);
			}else{
				FINANCE_INFO("ReqQryTradingAccount Err For Not Login");
				return -1;
			}
		}

		void SetOnRspQryTradingAccountHandler(on_rtn_trading_account_ptr handler){
			pTraderApi->SetOnRspQryTradingAccountHandler(handler);
		}

		void SetOnRspQryInvestorPositionDetailHandler(on_rtn_position_detail_ptr handler){
			pTraderApi->SetOnRspQryInvestorPositionDetailHandler(handler);
		}

		void ReqQryOrder( std::string& InstrumentID, std::string& OrderSysID, std::string& InsertTimeStart,
				 std::string& InsertTimeEnd) {
			if (pTraderApi && pTraderApi->GetLoginStatus()) {
				FINANCE_INFO("ReqQryOrder");
				CThostFtdcQryOrderField query = {{0}};
				strcpy(query.BrokerID, m_brokerID.c_str());
				strcpy(query.InvestorID, m_investorID.c_str());
				pTraderApi->ReqQryOrder(&query);
			}
		}

		void ReqQryTrade()
		{
			if (pTraderApi && pTraderApi->GetLoginStatus()) {
				FINANCE_INFO("ReqQryTrade");
				CThostFtdcQryTradeField query = {{0}};
				strcpy(query.BrokerID, m_brokerID.c_str());
				strcpy(query.InvestorID, m_investorID.c_str());
				pTraderApi->ReqQryTrade(&query);
			}
		}

		void SubscribeOnRtnOrder(handler_ptr handler)
		{
			pTraderApi->SubscribeOnRtnOrder(handler);
		}

		void SubscribeOnRtnTrade(handler_ptr handler)
		{
			pTraderApi->SubscribeOnRtnTrade(handler);
		}
};

#endif
