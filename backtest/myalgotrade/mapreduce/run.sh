#!/usr/bin/env sh


source "/data1/ug_coin/.bashrc"
source "/data1/ug_coin/.bash_profile"

echo "pwd: `pwd`"

hdfs_user_path=$1
job_key=$2

hdfs_job_path=${hdfs_user_path}/${job_key}
hdfs_input="${hdfs_job_path}/input"
hdfs_output="${hdfs_job_path}/output"
hdfs_lib="${hdfs_job_path}/lib"
hdfs_packages="/user/ug_coin/nianqiang.jing/lib"

input_name=input_${job_key}.txt
output_name=output_${job_key}.txt

echo "running job: ${job_key}"
echo "hdfs job path: ${hdfs_job_path}"

hadoop fs -mkdir ${hdfs_job_path}
hadoop fs -mkdir ${hdfs_input}
hadoop fs -mkdir ${hdfs_lib}

sh refreshInput.sh ${input_name} ${hdfs_input}
sh putArchive.sh ${job_key} ${hdfs_lib}

mapper="mapper.py"
reducer="reducer.py"
tasks=`wc -l ${input_name}| cut -d ' ' -f 1`
map_tasks=$(($tasks/5))
reduce_tasks=$(($tasks/1000+1))
max_reduce=10
max_map=470

if [ ${map_tasks} -gt ${max_map} ]; then
  map_tasks=${max_map}
fi

if [ ${reduce_tasks} -gt ${max_reduce} ]; then
  reduce_tasks=${max_reduce}
fi



echo "map tasks: ${map_tasks}"
echo "reduce tasks: ${reduce_tasks}"

hadoop fs -rmr ${hdfs_output}
/opt/hadoop/bin/hadoop jar /opt/hadoop/hadoop-streaming-1.0.3.jar\
  -D mapred.map.tasks=${map_tasks} \
  -D mapred.reduce.tasks=${reduce_tasks} \
  -D mapred.job.priority=HIGH \
  -input ${hdfs_input} \
  -output ${hdfs_output} \
  -mapper ${mapper} \
  -file ${mapper} \
  -reducer ${reducer} \
  -file ${reducer} \
  -cacheArchive hdfs://YZSJHL18-25.opi.com${hdfs_lib}/mylib.tar.gz#mylib \
  -cacheArchive hdfs://YZSJHL18-25.opi.com${hdfs_packages}/packages.tar.gz#packages \

hadoop fs -cat ${hdfs_output}/part* > ${output_name}
