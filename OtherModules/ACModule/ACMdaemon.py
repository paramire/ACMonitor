import ACMsqlite
import time


a = ACMsqlite.acmDB('acm.bd','xbee_data.csv')
t = int(time.time())
ts = time.strftime('%Y-%m-%d %H:%M:%S')
g = {'code':1,'date_t':ts,'date_unix':t}
a.insert(a.INIT,**g)