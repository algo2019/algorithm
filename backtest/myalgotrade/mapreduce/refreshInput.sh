#!/usr/bin/env sh
input_name=$1
hdfs_path=$2

echo "refreshing input: ${input_name} to ${hdfs_path}"

hadoop fs -rm ${hdfs_path}/*
hadoop fs -put ${input_name} ${hdfs_path}
