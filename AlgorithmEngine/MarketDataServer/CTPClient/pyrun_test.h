#include "PrintProcessor.h"
#include "CSimpleHandler.h"
#include "RedisProcessor.h"
#include "InstrumnetGainer.h"
#include <unistd.h>


void test(char **res, int r_len, IMsgProcessor* p,  CSimpleHandler* cs) {
    string frontAddress = "tcp://180.168.146.187:10031";
    string marketAddress = "tcp://180.168.146.187:10030";

    string brokerID = "9999";
    string investorID = "066285";
    string password = "3735261";

    string redisHost = "127.0.0.1";
    string publishKey = "TickTest";

//    CSimpleHandler* cs = new CSimpleHandler(brokerID, investorID, password, frontAddress);

//    IMsgProcessor* p = new PrintProcessor();
//    IMsgProcessor* p = new RedisProcessor(redisHost, 6379, publishKey);
//    cs->InitProcess(p);
    sleep(2);
    cs->ReqInstrumentData(res, r_len);
    while (1) {
        sleep(10);
    }
}