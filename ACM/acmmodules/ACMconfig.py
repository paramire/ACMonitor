import ConfigParser, os

class acmConfigParser(object):
	config_data = {'xbee':{'port':'/dev/ttyO1',
                           'baud':9600,
                           'uart':None},
                   'sqlite':{'dbDir':'database/acm.bd',
                   	         'xbeeCSV':'files/xbee_data.csv'},
                   'mqtt':{'destIp':'127.0.0.1',
                           'destPort':1883,
                           'topicWill':'ACM/BBB/status',
                           'lastWill':'ERROR: BBB Lost'}}
	def __init__(self):
		self.config = ConfigParser.RawConfigParser()
		if not(os.path.isfile('acm.cfg')):
			for key in self.config_data:
				self.config.add_section(key)
				for conf in self.config_data[key]:
					self.config.set(key,conf,self.config_data[key][conf])
			with open('acm.cfg', 'w') as configfile:
				self.config.write(configfile)
		else:
			self.config.read('acm.cfg')

