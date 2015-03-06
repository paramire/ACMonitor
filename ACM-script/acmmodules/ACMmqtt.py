import mosquitto

class acmMQTT(object):
	"""acmMQTT object to manage MQTT ACM connection

	The object manage the MQTT connection 
	and the message to be sended, the message and the topic of
	each message posible

	This Module manage how to send the message and the structure
	of the messages, and the MQTT connection to MQTT broker

	topic (dictionary): Topics
	message (dictionary): Topics mesages

	"""
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
	           'status'      :"(%s) ARDUINO - CONNECTED, MODE: %s",
	           'statusDisc'  :"(%s) ARDUINO - DISCONNECTED",
	           'error'       :"(%s) BBB - ERROR: %s",
	           'clean'       :"(%s) BBB - CLEAN - DELETED ROWS: %s"}


	def __init__(self,ip,port=1883,prefix='',topic_will='',last_will='',looped=False):
		"""__init__ 

		MQTT object who manage the MQTT connection, save the IP, PORT,
		Topic of the Last Will and the Last Will
		added the option to have a MQTT looped connection for keep the
		connection
		If the Last Will isn't specified, doesn't set any

		Args:
			ip (string): IP of the MQTT Broker
			port (integer): Port number
			prefix =
			topic_will (string): Last Will message
			last_will (string): String with Last Will message
			looped (boolen): True if looped, False otherwise
		Returns:
			None
		"""
		self.ip = ip
		self.port = port
		if prefix != '':
			self.prefix = prefix + '/'
		else:
			self.prefix = prefix
		self.topic_will = prefix + 'ACM/' + topic_will
		self.last_will = last_will
		self.looped = looped
		self.mqttc = mosquitto.Mosquitto("ACM_pub")
		if last_will != '':
			self.mqttc.will_set(self.topic_will,self.last_will)
		self.mqttc.connect(self.ip,self.port,60,True)
		if self.looped:
			self.mqttc.loop_start()     
	
	def _make_message(self,tag,**kwargs):
		"""Internal function to make the specfici message

		Make the message reading the message and inserting the values.
		
		Args:
			tag (string): String with the message to send
			kwargs (dictionary): Values to insert in the Message 
		Returns:
			message (string): Final Message of the topic with values
		"""
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
		"""Sent init message
		Check if the amount of  Data is correct, generete the correct message
		and send the MQTT message
		
		Args:
			Kwargs(dictionary): Data that will be in the message
		Returns:
			None
		"""
		topic = self.prefix + self.topic['init']
		if len(kwargs) == 1:
			self.mqttc.publish(topic,self._make_message('init',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 1")

	def sendKeep(self,**kwargs):
		"""Sent Keep Alive message
		Check if the amount of  Data is correct, generete the correct message
		and send the MQTT message
		
		Args:
			Kwargs(dictionary): Data that will be in the message
		Returns:
			None
		"""
		topic = self.prefix + self.topic['keep']
		if len(kwargs) == 1:
			self.mqttc.publish(topic,self._make_message('keep',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 1")

	def sendAlarm(self,**kwargs):
		"""Sent Alarm message
		Check if the amount of  Data is correct, generete the correct message
		and send the MQTT message
		
		Args:
			Kwargs(dictionary): Data that will be in the message
		Returns:
			None
		"""
		topic = self.prefix + self.topic['alarm']
		if len(kwargs) == 1:
			self.mqttc.publish(topic,self._make_message('alarm',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 1")
	
	def sendAlarmOn(self,**kwargs):
		"""Sent Alarm On message
		Check if the amount of  Data is correct, generete the correct message
		and send the MQTT message
		
		Args:
			Kwargs(dictionary): Data that will be in the message
		Returns:
			None
		"""
		topic = self.prefix + self.topic['alarm_on']+kwargs['topic']
		if len(kwargs) == 3:
			self.mqttc.publish(topic,self._make_message('alarm_on',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 3")
	
	def sendFinish(self,**kwargs):
		"""Sent Finish message
		Check if the amount of  Data is correct, generete the correct message
		and send the MQTT message
		
		Args:
			Kwargs(dictionary): Data that will be in the message
		Returns:
			None
		"""
		topic = self.prefix + self.topic['finish']
		if len(kwargs) == 1:
			self.mqttc.publish(topic,self._make_message('finish',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 1")
	
	def sendStatus(self,**kwargs):
		"""Sent Status message
		Check if the amount of  Data is correct, generete the correct message
		and send the MQTT message
			
		Status Message can indicate if the Alarm is On or OFF, or if the Arduino it's 
		not sending messages

		Args:
			Kwargs(dictionary): Data that will be in the message
		Returns:
			None
		"""
		topic = self.prefix + self.topic['status']
		if len(kwargs) == 2 or len(kwargs) == 3:
			if kwargs['connected']:
				if kwargs['alert'] == 0:
					kwargs.update({'mode':"ALARM ON"})
				elif kwargs['alert'] == 1:
					kwargs.update({'mode':"ALARM OFF"})
				else:
					kwargs.update({'mode':"NOT CONNECTED"})
				self.mqttc.publish(topic,self._make_message('status',**kwargs))
			else:
				self.mqttc.publish(topic,self._make_message('statusDisc',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 2 or 3")

	def sendErrorXbee(self,**kwargs):
		"""Sent Error XBee message
		Check if the amount of  Data is correct, generete the correct message
		and send the MQTT message
		
		Args:
			Kwargs(dictionary): Data that will be in the message
		Returns:
			None
		"""
		topic = self.prefix + self.topic['error']
		if len(kwargs) == 2:
			self.mqttc.publish(topic,self._make_message('error',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 2")
	
	def sendClean(self,**kwargs):
		"""Sent Clean message
		Check if the amount of  Data is correct, generete the correct message
		and send the MQTT message
		
		Args:
			Kwargs(dictionary): Data that will be in the message
		Returns:
			None
		"""
		topic = self.prefix + self.topic['clean']
		if len(kwargs) == 2:
			self.mqttc.publish(topic,self._make_message('clean',**kwargs))
		else:
			raise ValueError("Wrong number of arguments, Expected 2")
	
	def close(self):
		"""Disconnect the MQTT server

		Disconnect the MQTT server, if the MQTT is looped(Connection open)
		close it
		
		Returns:
			None
		"""
		if self.looped:
			self.mqttc.loop_stop(force=True);
		self.mqttc.disconnect()