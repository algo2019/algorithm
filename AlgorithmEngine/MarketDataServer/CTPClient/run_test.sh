#!/bin/bash
export LD_LIBRARY_PATH=`readlink -f ../../lib`:$LD_LIBRARY_PATH
export PYTHONPATH=`readlink -f ../..`:$PYTHONPATH
cd target
# ./CTPClientRun ../dev.json
./CTPClientRun ../donghai.conf
