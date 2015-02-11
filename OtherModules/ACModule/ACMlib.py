from datetime import datetime
import serial, time
import ACMsqlite, ACMXbee
#, ACMsnmp
#from xbee import Xbee, ZigBee

class acm(object)

def __init__(self):
	#OPEN UART
	self.xbee_acm = ACMXbee.acmXbee('/dev/tty01','9600',endpoint)
	#OPEN SQLITe
	self.db_acm = ACMsqlite.acmDB("acm.bd","xbee_data.csv")
	if db_acm.check():
		print "SQLite" + str(db_acm.nameDB) + "is Open"
	#Open and Check Arduino
	#self.xbee = Xbee()

def get_time():
	var = {}
	var['unix'] = time.time()
	var['date'] = time.strftime('%Y-%m-%d %H:%M:%S')
	return var


def time_request(self,response):
	#GETTING DATA
	code = response['code']
	ts = get_time()
	
	#Send TIME PACKET
	xbee_acm.send_time(code, ts_unix)
	db_acm.insert(db_acm.INIT,'code'=code,'date_t'=ts['date'],'date_unix'=ts['unix'])

def alarm_request():
	#Xbee Handle
	code = 0
	a_ts_unix = 0
	ts_unix = int(time.time()) #GET XBEE TIMESTAMP
	ts_date = time.strftime('%Y-%m-%d %H:%M:%S')
	db_acm.insert(db_acm.INIT,'code'=0,'date_t'=time['date'],'date_unix'=time['unix'],'a_ts_unix'=a_ts_unix)
	#make SNMP TRAP	
	pass

def alarm_on_request():
	#Xbee Handle
	code = 0;
	status = 0;
	a_ts_unix = 0;
	ts_unix = int(time.time()) #GET XBEE TIMESTAMP
	ts_date = time.strftime('%Y-%m-%d %H:%M:%S')
	db_acm.insert(db_acm.INIT,'code'=0,'date_t'=ts_date,'date_unix'=ts_unix,'a_ts_unix'=a_ts_unix)
	#make SNMP TRAP
	pass

def keep_alive():
	code = 0;
	ts_unix = int(time.time()) #GET XBEE TIMESTAMP
	ts_date = time.strftime('%Y-%m-%d %H:%M:%S')
	db_acm.insert(db_acm.INIT,'code'=0,'date_t'=ts_date,'date_unix'=ts_unix)
	pass


