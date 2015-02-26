import ConfigParser, os

class acmConfigParser():
	config_data = {'xbee':{'port':'/dev/ttyO1',
                           'baud':9600,
                           'uart':None},
                   'sqlite':{'db_dir':'database/acm.bd',
                   	         'xbee_csv':'files/xbee_data.csv'},
                   'mqtt':{'dest_ip':'localhost',
                           'dest_port':1883,
                           'topic_will':'ACM/BBB/status',
                           'last_will':'ERROR: BBB Lost'},
                   'general':{'month_gap':3,
                              'sleep_time':150}}
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

	def getConf(self,section,*args):
		data = {}
		if self.config.has_section(section):
			for row in self.config_data[section]:
				if row not in args:
					if self.config.has_option(section,row):
						data[row] = self.config.get(section,row)
					else:
						raise ValueError('No configuration for %s, %s', (row,section))
		return data

	def getGeneralConf(self,general_conf):
		if self.config.has_option('general',general_conf):
			return self.config.get('general',general_conf)
		else:
			raise ValueError('No configuration for %s,%s', (general_conf,'general')) 