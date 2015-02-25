import mosquitto

class acmMQTT(object):

	topic = {'init'      :"ACM/arduino/init",
	         'keep'      :"ACM/arduino/keepalive",
	         'alarm'     :"ACM/arduino/alarm/general",
	         'alarm_on'  :"ACM/arduino/alarm_on/",
	         'finish'    :"ACM/arduino/finish",
	         'status'    :"ACM/arduino/status",
	         'error'     :"ACM/BBB/error",
	         'clean'     :"ACM/BBB/clean"}

	message = {'init'        :"(%s) ARDUINO - init",
	           'keep'        :"(%s) ARDUINO - keep_alive",
	           'alarm'       :"(%s) ARDUINO - GENERAL ALARM",
	           'alarm_on'    :"(%s) ARDUINO - ALARM (%s): (%s)",
	           'finish'      :"(%s) ARDUINO - GENERAL ALARM FINISH",
	           'status'      :"(%s) ARDUINO - CONNECTED, ALARM: %s",
	           'statusDisc'  :"(%s) ARDUINO - DISCONNECTED",
	           'error'       :"(%s) BBB - ERROR: %s",
	           'clean'       :"(%s) BBB - CLEAN - DELETED ROWS: %s"}


	def __init__(self,ip,port=1883,topic_will='',last_will='',looped=False):
		self.ip = ip
		self.port = port
		self.topic_will = 'ACM/' + topic_will
		self.last_will = last_will
		self.looped = looped
		self.mqttc = mosquitto.Mosquitto("ACM_pub")
		if last_will != '':
			self.mqttc.will_set(self.topic_will,self.last_will)
		self.mqttc.connect(self.ip,self.port,60,True)
		if self.looped:
			self.mqttc.loop_start()     
	
	def _make_message(self,tag,**kwargs):
		if tag == 'init':
			message = self.message['init'] % (kwargs['time'])
		elif tag == 'keep':
			message = self.message['keep'] % (kwargs['time'])
		elif tag == 'alarm':
			message = self.message['alarm'] % (kwargs['time'])
		elif tag == 'alarm_on':
			message = self.message['alarm_on'] % (kwargs['time'],kwargs['topic'],kwargs['value'])
		elif tag == 'finish':
			message = self.message['finish'] % (kwargs['time'])
		elif tag == 'status':
			message = self.message['status'] % (kwargs['time'],kwargs['mode'])
		elif tag == 'statusDisc':
			message = self.message['statusDisc'] % (kwargs['time'])
		elif tag == 'error':
			message = self.message['error'] % (kwargs['time'],kwargs['error'])
		elif tag == 'clean':
			message = self.message['clean'] % (kwargs['time'],kwargs['rows'])
		return message

	def sendInit(self,**kwargs):
		if len(kwargs) == 1:
			self.mqttc.publish(self.topic['init'],self._make_message('init',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 1")

	def sendKeep(self,**kwargs):
		if len(kwargs) == 1:
			self.mqttc.publish(self.topic['keep'],self._make_message('keep',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 1")

	def sendAlarm(self,**kwargs):
		if len(kwargs) == 1:
			self.mqttc.publish(self.topic['alarm'],self._make_message('alarm',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 1")
	
	def sendAlarmOn(self,**kwargs):
		if len(kwargs) == 3:
			self.mqttc.publish(self.topic['alarm_on']+kwargs['topic'],self._make_message('alarm_on',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 3")
	
	def sendFinish(self,**kwargs):
		if len(kwargs) == 1:
			self.mqttc.publish(self.topic['finish'],self._make_message('finish',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 1")
	
	def sendStatus(self,**kwargs):
		if len(kwargs) == 2 or len(kwargs) == 3:
			if kwargs['connected']:
				if kwargs['alert']:
					kwargs.update({'mode':"ON"})
				else:
					kwargs.update({'mode':"OFF"})
				self.mqttc.publish(self.topic['status'],self._make_message('status',**kwargs))
			else:
				self.mqttc.publish(self.topic['status'],self._make_message('statusDisc',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 2 or 3")

	def sendErrorXbee(self,**kwargs):
		if len(kwargs) == 2:
			self.mqttc.publish(self.topic['error'],self._make_message('error',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 2")
	
	def sendClean(self,**kwargs):
		if len(kwargs) == 2:
			self.mqttc.publish(self.topic['clean'],self._make_message('clean',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 2")
	
	def close(self):
		if self.looped:
			self.mqttc.loop_stop(force=True);
		self.mqttc.disconnect()