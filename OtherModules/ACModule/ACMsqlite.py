import sqlite3, csv, os

class acmDB(object):

	def __init__(self, nameDB, fileCSV ):
		self.ENDPOINT = 1000
		self.INIT = 1001
		self.ALARM = 1002
		self.ALARM_ON = 1003
		self.KEEP_ALIVE = 1004
		self.nameDB = nameDB
		self.fileCSV = fileCSV
		#self.cursor_ACM = self.conn.cursor()
		if not(os.path.isfile(nameDB)):
			self.conn = sqlite3.connect(self.nameDB)
			self.prepare()
			self.csv_bulk()
		else:
			self.conn = sqlite3.connect(self.nameDB)		

	def prepare(self):
		cursor_ACM = self.conn.cursor()
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS endpoint(id INTEGER PRIMARY KEY, code INTEGER, type TEXT, dest_high TEXT, dest_low TEXT)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS init(id INTEGER PRIMARY KEY, code INTEGER, date_t TEXT, date_unix INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS alarm(id INTEGER PRIMARY KEY, code INTEGER, date_t TEXT, date_unix INTEGER, a_date_unix INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS alarm_on(id INTEGER PRIMARY KEY,name TEXT, scan INTEGER,date_t TEXT, date_unix INTEGER, a_date_unix INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS keep_alive(code INTEGER,date_t TEXT, date_unix INTEGER)''')
		self.conn.commit()
	
	def csv_bulk(self):
		with open(self.fileCSV,'r') as f:
				reader = csv.reader(f)
				for row in reader:
					row_d = dict(zip(('code','type','dest_high','dest_low'),row))
					self.insert(self.ENDPOINT,**row_d)


	def insert(self, tag, **args ):
		cursor_ACM = self.conn.cursor()
		if tag ==  self.ENDPOINT:
			if len(args) == 4:
				cursor_ACM.execute('''INSERT INTO endpoint VALUES (null,?,?,?,?)''',(args['code'],args['type'],args['dest_high'],args['dest_low']))
			else:
				print "Error INSERT " + str(self.ENDPOINT)
		elif tag == self.INIT:
			if len(args) == 3:
				print cursor_ACM.execute('''INSERT INTO init VALUES (null,?,?,?)''',(args['code'],args['date_t'],args['date_unix']))
			else:
				print "Error INSERT " + str(self.INIT)
		elif tag == self.ALARM:
			if len(args) == 4:
				cursor_ACM.execute('INSERT INTO alarm VALUES (null,?,?,?,?,?)',(args["code"],args["date_t"],args["date_unix"],args["a_date_unix"]))
			else:
				print "Error INSERT " + str(self.ALARM)
		elif tag == self.ALARM_ON:
			if len(args) == 5:
				cursor_ACM.execute('INSERT INTO alarm_on VALUES (null,?,?,?,?,?)',(args["name"],args["scan"],args["date_t"],args["date_unix"],args["a_date_unix"]))
			else:
				print "Error INSERT " + str(self.ALARM_ON)
		elif tag == self.KEEP_ALIVE:
			if len(args) == 3:
				cursor_ACM.execute('INSERT INTO keep_alive VALUES (?,?,?)',(args["code"],args["date_t"],args["date_unix"]))
			else:
				print "Error INSERT " + str(self.KEEP_ALIVE)
		else:
			print "ERROR"

		self.conn.commit()

	def close(self):
		self.conn.close()

	def check(self):
		return os.path.isfile(self.nameDB)