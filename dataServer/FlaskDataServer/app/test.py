import urllib2
import cPickle as pickle
import json


r = urllib2.urlopen('http://127.0.0.1:5001/api/v1.0/dom_info?symbol=a&&start=20100101')
res = r.read()
print pickle.loads(str(json.loads(res)['res']))