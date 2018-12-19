#!/usr/bin/env bash


hadoop_client="ug_coin@10.4.19.81"
hadoop_path=$1
class_path=$2
config_path=$3
param_path=$4
feed_path=$5
result_path=$6
hdfs_user_path=$7
job_key=$8

job_path=${hadoop_path}/${job_key}
input_name=input_${job_key}.txt
output_name=output_${job_key}.txt

echo "\n------- committing hadoop job -------"
echo hadoop_client: ${hadoop_client}
echo hadoop_path: ${hadoop_path}
echo class_path: ${class_path}
echo param_path: ${param_path}
echo feed_path: ${feed_path}
echo output_path: ${result_path}
echo job_key: ${job_key}
echo hdfs_user_path: ${hdfs_user_path}

echo "\nputting files to ${hadoop_client}"
echo "job path: ${job_path}"
ssh ${hadoop_client} "mkdir ${job_path}"

scp ${class_path} ${config_path} ${feed_path} ${hadoop_client}:${job_path}
scp ${param_path} ${hadoop_client}:${hadoop_path}/${input_name}

echo "start running hadoop\n"

#ssh ${hadoop_client} "cd ${hadoop_path} && cat ${input_name} | python mapper.py | python reducer.py > ${output_name}"
ssh ${hadoop_client} "cd ${hadoop_path} && sh run.sh ${hdfs_user_path} ${job_key}"

echo copying output from ${hadoop_client}:${hadoop_path}/${output_name} to
echo ${result_path}
scp ${hadoop_client}:${hadoop_path}/${output_name} ${result_path}
echo "------- hadoop job done -------\n"
