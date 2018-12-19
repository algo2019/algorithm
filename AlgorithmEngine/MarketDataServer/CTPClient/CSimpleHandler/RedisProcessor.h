#ifndef __Redis_Processor__
#define __Redis_Processor__


#include <hiredis/hiredis.h>

#include "CSimpleHandler.h"
#include "ThostFtdcMdApi.h"


class RedisProcessor : public IMsgProcessor
{
    public:
        RedisProcessor(string& host, int port, string& publish_key){
            m_RedisContext = redisConnect(host.c_str(), port);
            sprintf(m_publish_key, "%s", publish_key.c_str());
        }

        virtual void process(CThostFtdcDepthMarketDataField *futureData){
            char buffer[5024];
            if(futureData->ClosePrice > 100000000){
              futureData->ClosePrice = 0.0;
            }
            if(futureData->SettlementPrice > 100000000){
              futureData->SettlementPrice = 0.0;
            }
            if(futureData->OpenPrice > 100000000){
              futureData->OpenPrice = 0.0;
            }
            if(futureData->HighestPrice > 100000000){
              futureData->HighestPrice = 0.0;
            }
            if(futureData->LowestPrice > 100000000){
              futureData->LowestPrice = 0.0;
            }
            sprintf(buffer,"TradingDay#%s|InstrumentID#%s|ExchangeID#%s|LastPrice#%lf|PreSettlementPrice#%lf|PreClosePrice#%lf|OpenPrice#%lf|HighestPrice#%lf|LowestPrice#%lf|Volume#%d|OpenInterest#%lf|ClosePrice#%lf|SettlementPrice#%lf|UpperLimitPrice#%lf|LowerLimitPrice#%lf|UpdateTime#%s.%d|BidPrice1#%lf|BidVolume1#%d|AskPrice1#%lf|AskVolume1#%d\0",
                                    futureData->TradingDay,
                                    futureData->InstrumentID,
                                    futureData->ExchangeID,
                                    futureData->LastPrice,
                                    futureData->PreSettlementPrice,
                                    futureData->PreClosePrice,
                                    futureData->OpenPrice,
                                    futureData->HighestPrice,
                                    futureData->LowestPrice,
                                    futureData->Volume,
                                    futureData->OpenInterest,
                                    futureData->ClosePrice,
                                    futureData->SettlementPrice,
                                    futureData->UpperLimitPrice, futureData->LowerLimitPrice,
                                    futureData->UpdateTime, futureData->UpdateMillisec,
                                    futureData->BidPrice1, futureData->BidVolume1,
                                    futureData->AskPrice1, futureData->AskVolume1);
            char temp[5000];
            sprintf(temp, "PUBLISH %s.%s %s\0", m_publish_key, futureData->InstrumentID, buffer);
            redisCommand(m_RedisContext, temp);
        }

     private:
        char m_publish_key[20];
        redisContext* m_RedisContext;
};


#endif