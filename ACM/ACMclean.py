import ACMsqlite, ACMmqtt
import time
"""
Name: alarm_trigger

Check if a Alarm On, checking that the last Alarm is before the
Last finish entr

Return:
	- True, alarm is off
	- Flase, alarm is on 
"""
def alarm_trigger(acm_sqlite):
	if acm_sqlite.is_empty(0xAA) | acm_sqlite.is_empty(0x55):
		max_id_alarm = acm_sqlite.select(0x55,fields='MAX(id)')[0]
		max_id_finish = acm_sqlite.select(0xAA,fields='MAX(id)')[0]
		print max_id_alarm 
		print max_id_finish
		alarm = acm_sqlite.select(0x55,fields='date_u',where='id = ' + str(max_id_alarm[0]),fetch_one=True)
		finish = acm_sqlite.select(0xAA,fields='date_u',where='id = ' + str(max_id_finish[0]),fetch_one=True)

		if alarm[0] > finish[0]:
			return True
		else:
			return False
	return True
"""
Name: Main

Delete the Database entry 3 month Old
If the System is receving messages wait 2 min until
check again

Return: Noneb
"""
def main():
	#3 Month
	month_gap = 2592000*3
	acm_sqlite = ACMsqlite.acmDB('database/acm.bd','files/xbee_data.csv')
	if acm_sqlite.check():
		print "SQLite " + str(acm_sqlite.nameDB) + " is Open"
	acm_mqtt = ACMmqtt.acmMQTT('127.0.0.1',1883,looped=False)
	
	while True:
		if alarm_trigger(acm_sqlite):
			now = int(time.time()) - month_gap
			query = 'date_u < ' + str(now)
			value = 0
			try:
				value += acm_sqlite.delete(0x0F,where=query)
				value += acm_sqlite.delete(0x21,where=query)
				value += acm_sqlite.delete(0xFF,where=query)
				value += acm_sqlite.delete(0x55,where=query)
				value += acm_sqlite.delete(0x56,where=query)
				value += acm_sqlite.delete(0xAA,where=query)
				acm_mqtt.sendTopic('clean',time=now,value=value)
			except Exception, e:
				raise ValueError('Error: Deleting from SQLite',e)
			finally:
				break
		else:
			time.sleep(120)

if __name__ == '__main__':
	main()