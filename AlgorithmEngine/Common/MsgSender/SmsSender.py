import urllib
from BaseSender import BaseSender
import abc


class SmsSender(BaseSender):
    __metaclass__ = abc.ABCMeta

    PhoneSenderUrl = 'http://sms.notify.d.xiaonei.com:2000/receiver?'

    def sms_sender(self, receivers, msg):
        if type(receivers) in {str, unicode}:
            receivers = [receivers]
        for receiver in receivers:
            params = urllib.urlencode({'number': receiver, 'message': msg})
            urllib.urlopen(self.PhoneSenderUrl + params)
