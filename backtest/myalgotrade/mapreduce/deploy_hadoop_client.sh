#!/usr/bin/env bash

hadoop_client="ug_coin@10.4.19.81"

module_path=$1
deploy_path=$2


cd ${module_path}
scp putArchive.sh putPackages.sh refreshInput.sh run.sh mapper.py reducer.py ${hadoop_client}:${deploy_path}


