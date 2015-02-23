import mosquitto

class acmMQTT(object):

	topic = {'init'    :"ACM/arduino/init",
	         'keep'    :"ACM/arduino/keepalive",
	         'alarm'   :"ACM/arduino/alarm/general",
	         'alarm_on':"ACM/arduino/alarm_on/",
	         'finish'  :"ACM/arduino/finish",
	         'error'   :"ACM/BBB/error",
	         'clean'   :"ACM/BBB/clean"}


	def __init__(self,ip,port,topic_will='',last_will='',looped=False):
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

	def sendTopic(self,tag,**kwargs):
		if tag == 'init':
			self.mqttc.publish(self.topic['init'], "("+ str(kwargs['time']) + ") ARDUINO init" ) 
		elif tag == 'keep':
			self.mqttc.publish(self.topic['keep'], "("+ str(kwargs['time']) + ") ARDUINO keep_alive;" ) 
		elif tag == 'alarm':
			self.mqttc.publish(self.topic['alarm'], "("+ str(kwargs['time']) + ") GENERAL ALARM") 
		elif tag == 'alarm_on':
			self.mqttc.publish(self.topic['alarm_on'] + kwargs['topic'],"("+ str(kwargs['time']) + ") ALARM" + kwargs['topic']) 
		elif tag == 'error':
			self.mqttc.publish(self.topic['error'], "("+ str(kwargs['time']) + ") BeagleBone ERROR")          
		elif tag == 'finish':
			self.mqttc.publish(self.topic['finish'], "("+str(kwargs['time']) + ") GENERAL ALARM FINISH")
		elif tag == 'clean':
			self.mqttc.publish(self.topic['clean'], "("+str(kwargs['time']) + ") SQLite Clean, Rows Deleted: " + str(kwargs['value'])) 
		else:
			raise ValueError("No topic with " + tag)       

	def close(self):
		if self.looped:
			self.mqttc.loop_stop(force=True);