# coding=utf-8
from ThostFtdcUserApiDataType cimport *

cdef extern from "ThostFtdcUserApiStruct.h":
    ctypedef struct CThostFtdcTradeField:
        #经纪公司代码
        TThostFtdcBrokerIDType    BrokerID;
        #投资者代码
        TThostFtdcInvestorIDType    InvestorID;
        #合约代码
        TThostFtdcInstrumentIDType    InstrumentID;
        #报单引用
        TThostFtdcOrderRefType    OrderRef;
        #用户代码
        TThostFtdcUserIDType    UserID;
        #交易所代码
        TThostFtdcExchangeIDType    ExchangeID;
        #成交编号
        TThostFtdcTradeIDType    TradeID;
        #买卖方向
        TThostFtdcDirectionType    Direction;
        #报单编号
        TThostFtdcOrderSysIDType    OrderSysID;
        #会员代码
        TThostFtdcParticipantIDType    ParticipantID;
        #客户代码
        TThostFtdcClientIDType    ClientID;
        #交易角色
        TThostFtdcTradingRoleType    TradingRole;
        #合约在交易所的代码
        TThostFtdcExchangeInstIDType    ExchangeInstID;
        #开平标志
        TThostFtdcOffsetFlagType    OffsetFlag;
        #投机套保标志
        TThostFtdcHedgeFlagType    HedgeFlag;
        #价格
        TThostFtdcPriceType    Price;
        #数量
        TThostFtdcVolumeType    Volume;
        #成交时期
        TThostFtdcDateType    TradeDate;
        #成交时间
        TThostFtdcTimeType    TradeTime;
        #成交类型
        TThostFtdcTradeTypeType    TradeType;
        #成交价来源
        TThostFtdcPriceSourceType    PriceSource;
        #交易所交易员代码
        TThostFtdcTraderIDType    TraderID;
        #本地报单编号
        TThostFtdcOrderLocalIDType    OrderLocalID;
        #结算会员编号
        TThostFtdcParticipantIDType    ClearingPartID;
        #业务单元
        TThostFtdcBusinessUnitType    BusinessUnit;
        #序号
        TThostFtdcSequenceNoType    SequenceNo;
        #交易日
        TThostFtdcDateType    TradingDay;
        #结算编号
        TThostFtdcSettlementIDType    SettlementID;
        #经纪公司报单编号
        TThostFtdcSequenceNoType    BrokerOrderSeq;
        #成交来源
        TThostFtdcTradeSourceType    TradeSource;

    ctypedef struct CThostFtdcOrderField:
        #经纪公司代码
        TThostFtdcBrokerIDType    BrokerID;
        #投资者代码
        TThostFtdcInvestorIDType    InvestorID;
        #合约代码
        TThostFtdcInstrumentIDType    InstrumentID;
        #报单引用
        TThostFtdcOrderRefType    OrderRef;
        #用户代码
        TThostFtdcUserIDType    UserID;
        #报单价格条件
        TThostFtdcOrderPriceTypeType    OrderPriceType;
        #买卖方向
        TThostFtdcDirectionType    Direction;
        #组合开平标志
        TThostFtdcCombOffsetFlagType    CombOffsetFlag;
        #组合投机套保标志
        TThostFtdcCombHedgeFlagType    CombHedgeFlag;
        #价格
        TThostFtdcPriceType    LimitPrice;
        #数量
        TThostFtdcVolumeType    VolumeTotalOriginal;
        #有效期类型
        TThostFtdcTimeConditionType    TimeCondition;
        #GTD日期
        TThostFtdcDateType    GTDDate;
        #成交量类型
        TThostFtdcVolumeConditionType    VolumeCondition;
        #最小成交量
        TThostFtdcVolumeType    MinVolume;
        #触发条件
        TThostFtdcContingentConditionType    ContingentCondition;
        #止损价
        TThostFtdcPriceType    StopPrice;
        #强平原因
        TThostFtdcForceCloseReasonType    ForceCloseReason;
        #自动挂起标志
        TThostFtdcBoolType    IsAutoSuspend;
        #业务单元
        TThostFtdcBusinessUnitType    BusinessUnit;
        #请求编号
        TThostFtdcRequestIDType    RequestID;
        #本地报单编号
        TThostFtdcOrderLocalIDType    OrderLocalID;
        #交易所代码
        TThostFtdcExchangeIDType    ExchangeID;
        #会员代码
        TThostFtdcParticipantIDType    ParticipantID;
        #客户代码
        TThostFtdcClientIDType    ClientID;
        #合约在交易所的代码
        TThostFtdcExchangeInstIDType    ExchangeInstID;
        #交易所交易员代码
        TThostFtdcTraderIDType    TraderID;
        #安装编号
        TThostFtdcInstallIDType    InstallID;
        #报单提交状态
        TThostFtdcOrderSubmitStatusType    OrderSubmitStatus;
        #报单提示序号
        TThostFtdcSequenceNoType    NotifySequence;
        #交易日
        TThostFtdcDateType    TradingDay;
        #结算编号
        TThostFtdcSettlementIDType    SettlementID;
        #报单编号
        TThostFtdcOrderSysIDType    OrderSysID;
        #报单来源
        TThostFtdcOrderSourceType    OrderSource;
        #报单状态
        TThostFtdcOrderStatusType    OrderStatus;
        #报单类型
        TThostFtdcOrderTypeType    OrderType;
        #今成交数量
        TThostFtdcVolumeType    VolumeTraded;
        #剩余数量
        TThostFtdcVolumeType    VolumeTotal;
        #报单日期
        TThostFtdcDateType    InsertDate;
        #委托时间
        TThostFtdcTimeType    InsertTime;
        #激活时间
        TThostFtdcTimeType    ActiveTime;
        #挂起时间
        TThostFtdcTimeType    SuspendTime;
        #最后修改时间
        TThostFtdcTimeType    UpdateTime;
        #撤销时间
        TThostFtdcTimeType    CancelTime;
        #最后修改交易所交易员代码
        TThostFtdcTraderIDType    ActiveTraderID;
        #结算会员编号
        TThostFtdcParticipantIDType    ClearingPartID;
        #序号
        TThostFtdcSequenceNoType    SequenceNo;
        #前置编号
        TThostFtdcFrontIDType    FrontID;
        #会话编号
        TThostFtdcSessionIDType    SessionID;
        #用户端产品信息
        TThostFtdcProductInfoType    UserProductInfo;
        #状态信息
        TThostFtdcErrorMsgType    StatusMsg;
        #用户强评标志
        TThostFtdcBoolType    UserForceClose;
        #操作用户代码
        TThostFtdcUserIDType    ActiveUserID;
        #经纪公司报单编号
        TThostFtdcSequenceNoType    BrokerOrderSeq;
        #相关报单
        TThostFtdcOrderSysIDType    RelativeOrderSysID;
        #郑商所成交数量
        TThostFtdcVolumeType    ZCETotalTradedVolume;
        #互换单标志
        TThostFtdcBoolType    IsSwapOrder;
        #营业部编号
        TThostFtdcBranchIDType    BranchID;
        #投资单元代码
        TThostFtdcInvestUnitIDType    InvestUnitID;
        #资金账号
        TThostFtdcAccountIDType    AccountID;
        #币种代码
        TThostFtdcCurrencyIDType    CurrencyID;
        #IP地址
        TThostFtdcIPAddressType    IPAddress;
        #Mac地址
        TThostFtdcMacAddressType    MacAddress;

    
    #资金账户
    ctypedef struct CThostFtdcTradingAccountField:
        #经纪公司代码
        TThostFtdcBrokerIDType	BrokerID;
        #投资者帐号
        TThostFtdcAccountIDType	AccountID;
        #上次质押金额
        TThostFtdcMoneyType	PreMortgage;
        #上次信用额度
        TThostFtdcMoneyType	PreCredit;
        #上次存款额
        TThostFtdcMoneyType	PreDeposit;
        #上次结算准备金
        TThostFtdcMoneyType	PreBalance;
        #上次占用的保证金
        TThostFtdcMoneyType	PreMargin;
        #利息基数
        TThostFtdcMoneyType	InterestBase;
        #利息收入
        TThostFtdcMoneyType	Interest;
        #入金金额
        TThostFtdcMoneyType	Deposit;
        #出金金额
        TThostFtdcMoneyType	Withdraw;
        #冻结的保证金
        TThostFtdcMoneyType	FrozenMargin;
        #冻结的资金
        TThostFtdcMoneyType	FrozenCash;
        #冻结的手续费
        TThostFtdcMoneyType	FrozenCommission;
        #当前保证金总额
        TThostFtdcMoneyType	CurrMargin;
        #资金差额
        TThostFtdcMoneyType	CashIn;
        #手续费
        TThostFtdcMoneyType	Commission;
        #平仓盈亏
        TThostFtdcMoneyType	CloseProfit;
        #持仓盈亏
        TThostFtdcMoneyType	PositionProfit;
        #期货结算准备金
        TThostFtdcMoneyType	Balance;
        #可用资金
        TThostFtdcMoneyType	Available;
        #可取资金
        TThostFtdcMoneyType	WithdrawQuota;
        #基本准备金
        TThostFtdcMoneyType	Reserve;
        #交易日
        TThostFtdcDateType	TradingDay;
        #结算编号
        TThostFtdcSettlementIDType	SettlementID;
        #信用额度
        TThostFtdcMoneyType	Credit;
        #质押金额
        TThostFtdcMoneyType	Mortgage;
        #交易所保证金
        TThostFtdcMoneyType	ExchangeMargin;
        #投资者交割保证金
        TThostFtdcMoneyType	DeliveryMargin;
        #交易所交割保证金
        TThostFtdcMoneyType	ExchangeDeliveryMargin;
        #保底期货结算准备金
        TThostFtdcMoneyType	ReserveBalance;
        #币种代码
        TThostFtdcCurrencyIDType	CurrencyID;
        #上次货币质入金额
        TThostFtdcMoneyType	PreFundMortgageIn;
        #上次货币质出金额
        TThostFtdcMoneyType	PreFundMortgageOut;
        #货币质入金额
        TThostFtdcMoneyType	FundMortgageIn;
        #货币质出金额
        TThostFtdcMoneyType	FundMortgageOut;
        #货币质押余额
        TThostFtdcMoneyType	FundMortgageAvailable;
        #可质押货币金额
        TThostFtdcMoneyType	MortgageableFund;
        #特殊产品占用保证金
        TThostFtdcMoneyType	SpecProductMargin;
        #特殊产品冻结保证金
        TThostFtdcMoneyType	SpecProductFrozenMargin;
        #特殊产品手续费
        TThostFtdcMoneyType	SpecProductCommission;
        #特殊产品冻结手续费
        TThostFtdcMoneyType	SpecProductFrozenCommission;
        #特殊产品持仓盈亏
        TThostFtdcMoneyType	SpecProductPositionProfit;
        #特殊产品平仓盈亏
        TThostFtdcMoneyType	SpecProductCloseProfit;
        #根据持仓盈亏算法计算的特殊产品持仓盈亏
        TThostFtdcMoneyType	SpecProductPositionProfitByAlg;
        #特殊产品交易所保证金
        TThostFtdcMoneyType	SpecProductExchangeMargin;

    #响应信息
    ctypedef struct CThostFtdcRspInfoField:
        #错误代码
        TThostFtdcErrorIDType	ErrorID;
        #错误信息
        TThostFtdcErrorMsgType	ErrorMsg;



    #投资者持仓明细
    ctypedef struct CThostFtdcInvestorPositionDetailField:
        #合约代码
        TThostFtdcInstrumentIDType	InstrumentID;
        #经纪公司代码
        TThostFtdcBrokerIDType	BrokerID;
        #投资者代码
        TThostFtdcInvestorIDType	InvestorID;
        #投机套保标志
        TThostFtdcHedgeFlagType	HedgeFlag;
        #买卖
        TThostFtdcDirectionType	Direction;
        #开仓日期
        TThostFtdcDateType	OpenDate;
        #成交编号
        TThostFtdcTradeIDType	TradeID;
        #数量
        TThostFtdcVolumeType	Volume;
        #开仓价
        TThostFtdcPriceType	OpenPrice;
        #交易日
        TThostFtdcDateType	TradingDay;
        #结算编号
        TThostFtdcSettlementIDType	SettlementID;
        #成交类型
        TThostFtdcTradeTypeType	TradeType;
        #组合合约代码
        TThostFtdcInstrumentIDType	CombInstrumentID;
        #交易所代码
        TThostFtdcExchangeIDType	ExchangeID;
        #逐日盯市平仓盈亏
        TThostFtdcMoneyType	CloseProfitByDate;
        #逐笔对冲平仓盈亏
        TThostFtdcMoneyType	CloseProfitByTrade;
        #逐日盯市持仓盈亏
        TThostFtdcMoneyType	PositionProfitByDate;
        #逐笔对冲持仓盈亏
        TThostFtdcMoneyType	PositionProfitByTrade;
        #投资者保证金
        TThostFtdcMoneyType	Margin;
        #交易所保证金
        TThostFtdcMoneyType	ExchMargin;
        #保证金率
        TThostFtdcRatioType	MarginRateByMoney;
        #保证金率(按手数)
        TThostFtdcRatioType	MarginRateByVolume;
        #昨结算价
        TThostFtdcPriceType	LastSettlementPrice;
        #结算价
        TThostFtdcPriceType	SettlementPrice;
        #平仓量
        TThostFtdcVolumeType	CloseVolume;
        #平仓金额
        TThostFtdcMoneyType	CloseAmount;
