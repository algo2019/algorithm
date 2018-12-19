#ifndef __Print_Processor__
#define __Print_Processor__

#include "CSimpleHandler.h"
#include "ThostFtdcMdApi.h"


class PrintProcessor : public IMsgProcessor
{
    public:
        PrintProcessor(){};
        ~PrintProcessor(){};

        virtual void process(CThostFtdcDepthMarketDataField *futureData){
            printf("InstrumentID#%s\n", futureData->InstrumentID);
        }
};

#endif
