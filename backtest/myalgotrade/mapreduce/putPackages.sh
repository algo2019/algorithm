#!/usr/bin/env sh

path="/user/ug_coin/nianqiang.jing/lib/"
name="packages.tar.gz"
cd packages
rm $name
tar -zcvf $name *

hadoop fs -rm $path$name
hadoop fs -put $name $path
cd ..
