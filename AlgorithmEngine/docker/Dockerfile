FROM ubuntu:18.04
# MAINTAINER
MAINTAINER xingwang.zhang@renren-inc.com
# running required command
RUN apt-get update
RUN apt-get install git wget python gcc make g++ vim python-pip python-dev build-essential libmysqlclient-dev lsof cython net-tools -y
RUN pip install MySQL-python redis pyinstall psutil python-dateutil numpy pytz pandas interval
# change dir
WORKDIR /root
# environment set
RUN echo "export PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;36m\]\w\[\033[00m\]\$'" >> .bashrc
# service set
EXPOSE 80 5000
# build cmd
# docker build -t tradeplatform:xx .
# run cmd
# docker run --name trade -p 5000:5000 -p 60000:60000 -v `pwd`:/project --link mysql:mysql -d trade:0.0.7
