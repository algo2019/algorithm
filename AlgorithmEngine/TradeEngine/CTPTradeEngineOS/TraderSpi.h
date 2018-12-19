// TraderSpi.h: interface for the CTraderSpi class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_TRADERSPI_H__43862588_D1C0_4AB9_9356_68D1900AB786__INCLUDED_)
#define AFX_TRADERSPI_H__43862588_D1C0_4AB9_9356_68D1900AB786__INCLUDED_

#include "ThostFtdcTraderApi.h"
#include <hiredis/hiredis.h>
#include <stdio.h>
#include <string>
#include <map>
#include "Event.h"

typedef void (*on_rtn_trading_account_ptr)(CThostFtdcTradingAccountField *, CThostFtdcRspInfoField *, int, bool);
typedef void (*on_rtn_position_detail_ptr)(CThostFtdcInvestorPositionDetailField *pInvestorPositionDetail, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

class CTraderSpi : public CThostFtdcTraderSpi
{
public:
	CTraderSpi();
	~CTraderSpi();
	void Init(char* szAddress, char* redisAddress, int redisPorti, char* publishKey);
	bool GetLoginStatus() { return 	m_bLogedIn;}
	void SubscribeOnRtnOrder(handler_ptr );
	void SubscribeOnRtnTrade(handler_ptr );
	void SetOnRspQryTradingAccountHandler(on_rtn_trading_account_ptr );
	void SetOnRspQryInvestorPositionDetailHandler(on_rtn_position_detail_ptr);

public:
	///当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用。
	virtual void OnFrontConnected();
	
	///登录请求响应
	virtual void OnRspUserLogin(CThostFtdcRspUserLoginField *pRspUserLogin,	CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///投资者结算结果确认响应
	virtual void OnRspSettlementInfoConfirm(CThostFtdcSettlementInfoConfirmField *pSettlementInfoConfirm, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///请求查询合约响应
	virtual void OnRspQryInstrument(CThostFtdcInstrumentField *pInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///请求查询资金账户响应
	virtual void OnRspQryTradingAccount(CThostFtdcTradingAccountField *pTradingAccount, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///请求查询投资者持仓响应
	virtual void OnRspQryInvestorPosition(CThostFtdcInvestorPositionField *pInvestorPosition, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///报单录入请求响应
	virtual void OnRspOrderInsert(CThostFtdcInputOrderField *pInputOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///报单操作请求响应
	virtual void OnRspOrderAction(CThostFtdcInputOrderActionField *pInputOrderAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///错误应答
	virtual void OnRspError(CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///当客户端与交易后台通信连接断开时，该方法被调用。当发生这个情况后，API会自动重新连接，客户端可不做处理。
	virtual void OnFrontDisconnected(int nReason);
	
	///心跳超时警告。当长时间未收到报文时，该方法被调用。
	virtual void OnHeartBeatWarning(int nTimeLapse);
	
	///报单通知
	virtual void OnRtnOrder(CThostFtdcOrderField *pOrder);
	
	///成交通知
	virtual void OnRtnTrade(CThostFtdcTradeField *pTrade);

	///查询投资者持仓明细响应
	virtual void OnRspQryInvestorPositionDetail(CThostFtdcInvestorPositionDetailField *pInvestorPositionDetail, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///查询报单回报
	virtual void OnRspQryOrder(CThostFtdcOrderField *pOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///请求查询成交响应
    virtual void OnRspQryTrade(CThostFtdcTradeField *pTrade, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

public:
	///设置用户名和密码
	void SetUserInfo(const char* chUserName, const char* chPsw, const char* brokerID);
	///用户登录请求
	void ReqUserLogin();
	///投资者结算结果确认
	void ReqSettlementInfoConfirm();
	///请求查询合约
	void ReqQryInstrument();
	///请求查询资金账户
	int ReqQryTradingAccount(CThostFtdcQryTradingAccountField *pQryInvestorPositionDetail);
	///请求查询投资者持仓
	void ReqQryInvestorPosition();
	///请求查询投资者持仓明细
	int ReqQryInvestorPositionDetail(CThostFtdcQryInvestorPositionDetailField *pQryInvestorPositionDetail);
	///报单录入请求
    std::string ReqOrderInsert(char* chInstrment, double price, char offsetFlag, char direction, int volumn, char orderPriceType,
                  char timeCondition, char contingentCondition, int localRef);
	///报单操作请求
	void ReqOrderAction(const std::string& InstrumentID, int localRef, const int8_t ActionFlag);
	///请求报单
	void ReqQryOrder(CThostFtdcQryOrderField *pQryOrder);
    ///请求
    void ReqQryTrade(CThostFtdcQryTradeField *pQryTrade);

    TThostFtdcFrontIDType GetFrontID() {
        return m_frontID;
    }

    TThostFtdcSessionIDType GetSessionID() {
        return m_sessionID;
    }

private:
	// 是否收到成功的响应
	bool IsErrorRspInfo(CThostFtdcRspInfoField *pRspInfo);
	// 是否我的报单回报
	bool IsMyOrder(CThostFtdcOrderField *pOrder);
	// 是否正在交易的报单
	bool IsTradingOrder(CThostFtdcOrderField *pOrder);

	///日志输出函数
	void FormatLog(int nLevel, const char* strDomain, const char* strText, ...);

	char* getPositionKey(){
	    sprintf(m_positionKey, "%s.RemotePosition", m_publishKey);
      return m_positionKey;
	}

private:
    char m_positionKey[100];
    char *m_redisAddress;

    char* m_publishKey;

    int m_redisPort;
	///与服务器通信的API
	CThostFtdcTraderApi*		m_pUserApi;
	///前置编号
	TThostFtdcFrontIDType		m_frontID;
	///会话编号
	TThostFtdcSessionIDType		m_sessionID;
	///报单引用
	TThostFtdcOrderRefType		m_orderRef;
	///用户名
	TThostFtdcUserNameType		m_userName;
	///密码
	TThostFtdcPasswordType		m_password;
	///测试合约名
	TThostFtdcInstrumentIDType	m_instrument;

  	TThostFtdcBrokerIDType m_brokerID;
  
	///请求编号
	int							m_nRequestId;
	///开仓价
	double						m_dOpenPrice;
	///平仓价
	double						m_dClosePrice;
	///开平选择
	bool						m_bOpen;
	///是否登陆成功
	bool						m_bLogedIn;

	//m_nRequestId 与 local_ref 对照
  	std::map<int, int> orderRefNameMap;
  	std::map<int, int> nameOrderRefMap;
	Event *onRtnOrderEvent;
	Event *onRtnTradeEvent;
	on_rtn_trading_account_ptr m_OnRspQryTradingAccountHandler;
	on_rtn_position_detail_ptr m_OnRspQryInvestorPositionDetailHandler;
};

#endif // !defined(AFX_TRADERSPI_H__43862588_D1C0_4AB9_9356_68D1900AB786__INCLUDED_)
