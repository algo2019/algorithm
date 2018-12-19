# trade platform docker file

## 原始镜像

```
Ubuntu 18.04
```

## 环境配置

```shell
apt-get update
apt-get install git wget python gcc make g++
apt-get install vim
apt-get install python-pip python-dev build-essential
apt-get install  libmysqlclient-dev redis lsof cython net-tools 
pip install MySQL-python ipython redis flask flask_login flask_bootstrap
pip install tornado pyinstalle psutil
```

## Docker File 内容

```dockerfile
# base image
FROM ubuntu:18.04
# MAINTAINER
MAINTAINER xingwang.zhang@renren-inc.com
# running required command
RUN apt-get update
RUN apt-get install git wget python gcc make g++ vim python-pip python-dev build-essential libmysqlclient-dev redis lsof cython net-tools -y
RUN pip install MySQL-python redis ipython flask flask_login flask_bootstrap tornado
# conf files
ADD redis.conf /etc/redis/redis.conf
# change dir to /usr/local/src/nginx-1.12.2
WORKDIR /root
# environment set
RUN echo "export PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;36m\]\w\[\033[00m\]\$'" >> .bashrc 
# service set
RUN echo "service redis-server start" >> .bashrc
EXPOSE 80
EXPOSE 6379
# build cmd
# docker build -t tradeplatform:xx .
# run cmd
# docker run --name tradex -v ~:/project -p 6379:6379 -p 80:80 tradeplatform:xx
```

