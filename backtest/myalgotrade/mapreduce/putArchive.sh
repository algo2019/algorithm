#!/usr/bin/env sh

lib_path=$1
hdfs_path=$2
name="mylib.tar.gz"

echo "putting job libs from ${lib_path} to ${hdsf_path}"

cd ${lib_path}
rm ${name}
rm *.pyc
tar -zcf ${name} *

hadoop fs -rm ${hdfs_path}/${name}
hadoop fs -put ${name} ${hdfs_path}
cd ..
