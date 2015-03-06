import ConfigParser, os

class acmConfigParser():
	config_data = {'xbee':{'port':'/dev/ttyUSB0',
                           'baud':9600,
                           'uart':None},
                   'sqlite':{'db_dir':'database/acm.bd',
                   	         'xbee_csv':'files/xbee_data.csv'},
                   'mqtt':{'dest_ip':'localhost',
                           'dest_port':1883,
                           'topic_will':'ACM/BBB/status',
                           'last_will':'ERROR: BBB Lost',
                           'mqtt_prefix':'',
                           'client':'ACM_pub'},
                   'general':{'month_gap':3,
                              'sleep_time':150,
                              'gen_dir':'/home/ACM/ACM/ACM-script'}}
	def __init__(self):
		""" __init___ acmConfigParser

		Create a ConfigParser, then check if exist a configuration
		file, if don't, create a new one, if exist read the configurations

		Args:
			None
		Returns:
			None
		"""
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
		"""Get all the configuration of the specific configuration

		Retrieve all the configuration data in the file of the
		specific section
		it posible specify which field want to DON'T be retrieved

		Args:
			section (string): section string
			*args (Array): Array of configuration we don't want

		Returns:
			Array of the data	
		Raise:
			If don't exist configuration entry in the File
		"""
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
		"""Retrieve a general configuration

		Returns:
			Configuration data
		Raise:
			If don't exist configuration entry in the File
		"""
		if self.config.has_option('general',general_conf):
			return self.config.get('general',general_conf)
		else:
			raise ValueError('No configuration for %s,%s', (general_conf,'general')) 