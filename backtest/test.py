from myalgotrade.dataServerFeed.DomBarFeed import BarFeed

from dataServer import Conf
# Conf.CACHE = False

b = BarFeed('ag', '20161201', '20170327', '1m', 10, 3)

a = b
print b._BarFeed__bars['bu1706'][-1]['dateTime']

import dataServer
from dataServer import dataServer, d
from dataServer import Conf
