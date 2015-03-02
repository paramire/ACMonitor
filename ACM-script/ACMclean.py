import acmmodules.ACMsqlite as ACMsqlite
import acmmodules.ACMmqtt as ACMmqtt
import acmmodules.ACMconfig as ACMconfig
import time

def alarm_trigger(acm_sqlite):
	"""Check if the ALARM on

	Check if a Alarm On, checking the last Alarm value is before the
	Last finish value
	Args:
		acm_sqlite(Sqlite3 connection): Sqlite3 Database Connection	
	Returns:
		True, alarm is off, False otherwise 
	"""
	if acm_sqlite.is_empty(0xAA) or acm_sqlite.is_empty(0x55):
		max_id_alarm = acm_sqlite.select(0x55,fields='MAX(id)',fetch_one=True)
		max_id_finish = acm_sqlite.select(0xAA,fields='MAX(id)',fetch_one=True)
		alarm = acm_sqlite.select(0x55,fields='date_u',where='id = ' + str(max_id_alarm[0]),fetch_one=True)
		finish = acm_sqlite.select(0xAA,fields='date_u',where='id = ' + str(max_id_finish[0]),fetch_one=True)

		if alarm[0] < finish[0]:
			return True
		else:
			return False
	return True

def main():
	"""
	Main function

	Delete the Entry Database 3 month Old
	If the System is currently receving ALARM_ON messages wait 2 min until
	check again

	Args:
		None
	Returns:
		None
	"""
	#3 Month
	acm_config = ACMconfig.acmConfigParser()
	month_gap = 2592000*int(acm_config.getGeneralConf('month_gap'))
	acm_sqlite_conf = acm_config.getConf('sqlite')
	acm_sqlite = ACMsqlite.acmDB(acm_sqlite_conf['dbDir'],acm_sqlite_conf['xbeeCSV'])

	acm_mqtt_conf = acm_config.getConf('mqtt','topicWill','lastWill')
	acm_mqtt = ACMmqtt.acmMQTT(acm_mqtt_conf['dest_ip'],acm_mqtt_conf['dest_port'])

	
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
				acm_mqtt.sendClean(time=now,rows=value)
				acm_mqtt.close()
			except Exception, e:
				raise ValueError('Error: Deleting from SQLite',e)
			finally:
				break
		else:
			time.sleep(120)

if __name__ == '__main__':
	main()