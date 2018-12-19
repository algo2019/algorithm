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
	///���ͻ����뽻�׺�̨������ͨ������ʱ����δ��¼ǰ�����÷��������á�
	virtual void OnFrontConnected();
	
	///��¼������Ӧ
	virtual void OnRspUserLogin(CThostFtdcRspUserLoginField *pRspUserLogin,	CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///Ͷ���߽�����ȷ����Ӧ
	virtual void OnRspSettlementInfoConfirm(CThostFtdcSettlementInfoConfirmField *pSettlementInfoConfirm, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///�����ѯ��Լ��Ӧ
	virtual void OnRspQryInstrument(CThostFtdcInstrumentField *pInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///�����ѯ�ʽ��˻���Ӧ
	virtual void OnRspQryTradingAccount(CThostFtdcTradingAccountField *pTradingAccount, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///�����ѯͶ���ֲ߳���Ӧ
	virtual void OnRspQryInvestorPosition(CThostFtdcInvestorPositionField *pInvestorPosition, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///����¼��������Ӧ
	virtual void OnRspOrderInsert(CThostFtdcInputOrderField *pInputOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///��������������Ӧ
	virtual void OnRspOrderAction(CThostFtdcInputOrderActionField *pInputOrderAction, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///����Ӧ��
	virtual void OnRspError(CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);
	
	///���ͻ����뽻�׺�̨ͨ�����ӶϿ�ʱ���÷��������á���������������API���Զ��������ӣ��ͻ��˿ɲ�������
	virtual void OnFrontDisconnected(int nReason);
	
	///������ʱ���档����ʱ��δ�յ�����ʱ���÷��������á�
	virtual void OnHeartBeatWarning(int nTimeLapse);
	
	///����֪ͨ
	virtual void OnRtnOrder(CThostFtdcOrderField *pOrder);
	
	///�ɽ�֪ͨ
	virtual void OnRtnTrade(CThostFtdcTradeField *pTrade);

	///��ѯͶ���ֲ߳���ϸ��Ӧ
	virtual void OnRspQryInvestorPositionDetail(CThostFtdcInvestorPositionDetailField *pInvestorPositionDetail, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///��ѯ�����ر�
	virtual void OnRspQryOrder(CThostFtdcOrderField *pOrder, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

	///�����ѯ�ɽ���Ӧ
    virtual void OnRspQryTrade(CThostFtdcTradeField *pTrade, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast);

public:
	///�����û���������
	void SetUserInfo(const char* chUserName, const char* chPsw, const char* brokerID);
	///�û���¼����
	void ReqUserLogin();
	///Ͷ���߽�����ȷ��
	void ReqSettlementInfoConfirm();
	///�����ѯ��Լ
	void ReqQryInstrument();
	///�����ѯ�ʽ��˻�
	int ReqQryTradingAccount(CThostFtdcQryTradingAccountField *pQryInvestorPositionDetail);
	///�����ѯͶ���ֲ߳�
	void ReqQryInvestorPosition();
	///�����ѯͶ���ֲ߳���ϸ
	int ReqQryInvestorPositionDetail(CThostFtdcQryInvestorPositionDetailField *pQryInvestorPositionDetail);
	///����¼������
    std::string ReqOrderInsert(char* chInstrment, double price, char offsetFlag, char direction, int volumn, char orderPriceType,
                  char timeCondition, char contingentCondition, int localRef);
	///������������
	void ReqOrderAction(const std::string& InstrumentID, int localRef, const int8_t ActionFlag);
	///���󱨵�
	void ReqQryOrder(CThostFtdcQryOrderField *pQryOrder);
    ///����
    void ReqQryTrade(CThostFtdcQryTradeField *pQryTrade);

    TThostFtdcFrontIDType GetFrontID() {
        return m_frontID;
    }

    TThostFtdcSessionIDType GetSessionID() {
        return m_sessionID;
    }

private:
	// �Ƿ��յ��ɹ�����Ӧ
	bool IsErrorRspInfo(CThostFtdcRspInfoField *pRspInfo);
	// �Ƿ��ҵı����ر�
	bool IsMyOrder(CThostFtdcOrderField *pOrder);
	// �Ƿ����ڽ��׵ı���
	bool IsTradingOrder(CThostFtdcOrderField *pOrder);

	///��־�������
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
	///�������ͨ�ŵ�API
	CThostFtdcTraderApi*		m_pUserApi;
	///ǰ�ñ��
	TThostFtdcFrontIDType		m_frontID;
	///�Ự���
	TThostFtdcSessionIDType		m_sessionID;
	///��������
	TThostFtdcOrderRefType		m_orderRef;
	///�û���
	TThostFtdcUserNameType		m_userName;
	///����
	TThostFtdcPasswordType		m_password;
	///���Ժ�Լ��
	TThostFtdcInstrumentIDType	m_instrument;

  	TThostFtdcBrokerIDType m_brokerID;
  
	///������
	int							m_nRequestId;
	///���ּ�
	double						m_dOpenPrice;
	///ƽ�ּ�
	double						m_dClosePrice;
	///��ƽѡ��
	bool						m_bOpen;
	///�Ƿ��½�ɹ�
	bool						m_bLogedIn;

	//m_nRequestId �� local_ref ����
  	std::map<int, int> orderRefNameMap;
  	std::map<int, int> nameOrderRefMap;
	Event *onRtnOrderEvent;
	Event *onRtnTradeEvent;
	on_rtn_trading_account_ptr m_OnRspQryTradingAccountHandler;
	on_rtn_position_detail_ptr m_OnRspQryInvestorPositionDetailHandler;
};

#endif // !defined(AFX_TRADERSPI_H__43862588_D1C0_4AB9_9356_68D1900AB786__INCLUDED_)
