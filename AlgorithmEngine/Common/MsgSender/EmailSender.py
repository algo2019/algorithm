import smtplib
import abc
from email.header import Header
from email.mime.text import MIMEText
from Conf import EMAIL_DEFAULT
from BaseSender import BaseSender


class EmailSender(BaseSender):
    __metaclass__ = abc.ABCMeta

    def __init__(self, sender=None, smtpserver=None, username=None, password=None):
        self.__sender = sender or EMAIL_DEFAULT['sender']
        self.__smtpserver = smtpserver or EMAIL_DEFAULT['smtpserver']
        self.__username = username or EMAIL_DEFAULT['username']
        self.__password = password or EMAIL_DEFAULT['password']

    def send_email(self, receivers, subject, msg):
        if type(receivers) in {str, unicode}:
            receivers = [receivers]
        msg = MIMEText(msg, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = self.__sender
        msg['To'] = ','.join(receivers)
        smtp = smtplib.SMTP(self.__smtpserver)
        smtp.starttls()
        smtp.login(self.__username, self.__password)
        smtp.sendmail(self.__sender, receivers, msg.as_string())
        smtp.close()
