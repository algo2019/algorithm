#ifndef __MinDataProcess__H__
#define __MinDataProcess__H__

#include "CSimpleHandler.h"
#include "ThostFtdcMdApi.h"
#include "threadqueue.h"


class MinDataBar
{

};

class MinDataSender
{
    public:
        void process(MinDataBar& bar){};
};


class MinDataProcess : public IMsgProcessor
{
    public:
        MinDataProcess(MinDataSender& sender){
        	m_sender = sender;
        	m_queue = ThreadQueue();
        }

        void process(CThostFtdcDepthMarketDataField *futureData){

            printf("InstrumentID#%s\n", futureData->InstrumentID);
        }
    private:
    	MinDataSender m_sender;
    	ThreadQueue m_queue;

};


#endif