# coding=utf-8
import smtplib
import time
import urllib
from email.header import Header
from email.mime.text import MIMEText

from Tables import StrategyTable, WebAccountTable
from TradeEngine.GlobleConf import SysWidget
from Common.CommonLogServer.RedisLogService import Logger


class Config(object):
    """
    Config
    """
    Email = {
        "enable": True,
        'allReceiver': ['xingwang.zhang'],
        'xingwang.zhang': 'xingwang.zhang@renren-inc.com',
        'nianqiang.jing': 'nianqiang.jing3@renren-inc.com',
        'wei.liu': 'wei.liu@renren-inc.com',
        'liang.kong': 'liang.kong@renren-inc.com',
        "sender": {
            "smtpserver": "smtp.qq.com",
            "email": "xingwang.zhang@foxmail.com",
            "user": "515020386",
            "password": "kibcplzekpvvbifj"
        }
    }

    TelPhoneNum = {
        "enable": True,
        'allReceiver': ['xingwang.zhang'],
        'xingwang.zhang': '13552839840',
        'nianqiang.jing': '15120052913',
        'wei.liu': '13161975477',
    }

    # 同一主题,短信发送间隔
    MinSmsSendInterval = 60 * 1
    PhoneSenderUrl = 'http://sms.notify.d.xiaonei.com:2000/receiver?%s'
    #
    MinEMailSendInterval = 30


context = SysWidget.get_json_config()
if context is not None:
    try:
        Config.Email = context['error_sender']['email']
        Config.TelPhoneNum = context['error_sender']['telephone']
        print 'ErrSender: load json config ready!'

    except Exception as e:
        print 'ErrSender: load json config err:', str(e)


class SubSender(object):
    def __init__(self, contact):
        self.contact = contact

    def get_contacts(self, users):
        rt = set()
        for user in users:
            try:
                rt.add(self.contact[user])
            except:
                pass
        return list(rt)

    def send(self, subject, users, msg):
        pass


class StrategyErrSender(SubSender):
    def __init__(self, contact):
        super(StrategyErrSender, self).__init__(contact)
        self.st = StrategyTable.create()
        self.at = WebAccountTable.create()
        self.logger = Logger('Main', 'ErrSender', 'StrategyErrSender', 'StrategyErrSender')
        self.logger.INFO(msg='allReceiver:%s' % str(contact['allReceiver']))

    def get_use(self, pk, strategy_name):
        for user in self.at.get_all_username():
            if strategy_name in self.st.get_strategy_of_user(pk, [user]):
                return user
        return None

    def send_err(self, pk, strategy_name, msg):
        user = self.get_use(pk, strategy_name)
        if user is None:
            all_user = self.contact['allReceiver']
            self.logger.WARN('{}:user is None'.format(strategy_name))
        else:
            all_user = self.contact['allReceiver'] + [user]
        self.send('%s.%s' % (pk, strategy_name), all_user, msg)


class SmsSender(StrategyErrSender):
    def __init__(self):
        super(SmsSender, self).__init__(Config.TelPhoneNum)
        self.__last_send_time = {}
        self.__phone_sender_url = Config.PhoneSenderUrl

    @property
    def min_send_interval(self):
        try:
            return Config.MinSmsSendInterval
        except:
            return 60 * 60

    def send(self, subject, users, msg):
        if self.__last_send_time.get(subject) and time.time() - self.__last_send_time[subject] < self.min_send_interval:
            return
        send_msg = '%s \n\n %s' % (subject, msg)
        for receiver in self.get_contacts(users):
            params = urllib.urlencode({'number': receiver, 'message': send_msg})
            urllib.urlopen(self.__phone_sender_url % params)
        self.__last_send_time[subject] = time.time()

    def send_err(self, pk, strategy_name, msg):
        if not Config.TelPhoneNum.get('enable'):
            self.logger.info('sms send is disable')
            return
        if pk.startswith('ANALOG') or pk.startswith('DEV'):
            return
        super(SmsSender, self).send_err(pk, strategy_name, msg)


class EmailSender(StrategyErrSender):
    def __init__(self):
        super(EmailSender, self).__init__(Config.Email)
        self.__sender = Config.Email['sender']['email']
        self.__smtpserver = Config.Email['sender']['smtpserver']
        self.__username = Config.Email['sender']['user']
        self.__password = Config.Email['sender']['password']
        self.__last_send_time = {}

    @property
    def min_send_interval(self):
        try:
            return Config.MinEMailSendInterval
        except:
            return 1

    def send(self, subject, users, msg):
        if self.__last_send_time.get(subject) and time.time() - self.__last_send_time[subject] < self.min_send_interval:
            self.logger.info('last send time is on wait')
            return
        receiver = self.get_contacts(users)
        try:
            msg = MIMEText(msg, 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = self.__sender
            msg['To'] = ','.join(receiver)
            smtp = smtplib.SMTP(self.__smtpserver)
            smtp.starttls()
            smtp.login(self.__username, self.__password)
            self.logger.INFO('send email: %s %s %s' % (str(self.__sender), str(receiver), msg.as_string()))
            smtp.sendmail(self.__sender, receiver, msg.as_string())
            smtp.close()
        except Exception as e:
            self.logger.warn('send email err:{}'.format(str(e)))
        self.__last_send_time[subject] = time.time()

    def send_err(self, pk, strategy_name, msg):
        if not Config.Email.get('enable'):
            self.logger.info('email send is disable')
            return
        super(EmailSender, self).send_err(pk, strategy_name, msg)


class ErrMsgSenderMgr(object):
    def __init__(self):
        self.__logger = Logger('Main', 'ErrSender', 'MsgSenderMgr', 'MsgSenderMgr')
        self.__senders = []

    def add_sender(self, sender):
        if not hasattr(sender, 'send_err'):
            self.__logger.WARN('%s has no attr send_err' % str(sender))
            return

        self.__senders.append(sender)
        self.__logger.INFO('add sender %s' % str(sender))

    def remove_sender(self, sender):
        if sender in self.__senders:
            self.__senders.remove(sender)
            self.__logger.INFO('remove %s' % str(sender))
        else:
            self.__logger.WARN('remove %s not in senders' % str(sender))

    def send(self, pk, strategy_name, msg):
        for sender in self.__senders:
            try:
                sender.send_err(pk, strategy_name, msg)
            except Exception as e:
                self.__logger.warn('error in sender: {}'.format(str(e)))
