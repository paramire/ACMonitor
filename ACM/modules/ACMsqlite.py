import sqlite3, csv, os


class acmDB(object):
    
	table_name = {0x00:"endpoint",0x0F:"time",0x21:"keep_alive",0x55:"alarm",0x56:"alarm_on",0xAA:"finish",0xFF:"error",0x01:"other"}
	columns = {"endpoint":
	            [{'name':'code','type':'text'},
	             {'name':'type','type':'text'},
	             {'name':'dest_high','type':'text'},
	             {'name':'dest_low','type':'text'}],
	           "time":
	            [{'name':'code','type':'text'},
	             {'name':'date_t','type':'text'},
	             {'name':'date_u','type':'integer'}],
	           "keep_alive":
	            [{'name':'code','type':'text'},
	             {'name':'date_t','type':'text'},
	             {'name':'date_u','type':'integer'}],
	           "alarm":
	            [{'name':'code','type':'text'},
	             {'name':'date_t','type':'text'},
	             {'name':'date_u','type':'integer'},
	             {'name':'a_date_t','type':'text'},
	             {'name':'a_date_u','type':'integer'}],
	           "alarm_on":
	            [{'name':'code','type':'text'},
	             {'name':'name','type':'text'},
	             {'name':'scan','type':'integer'},
	             {'name':'date_t','type':'text'},
	             {'name':'date_u','type':'integer'},
	             {'name':'a_date_t','type':'integer'},
	             {'name':'a_date_u','type':'integer'}],
	           "finish":
	            [{'name':'code','type':'text'},
	             {'name':'date_t','type':'text'},
	             {'name':'date_u','type':'integer'},
	             {'name':'a_date_t','type':'text'},
	             {'name':'a_date_u','type':'integer'}],
	           "error":
	            [{'name':'code','type':'text'},
	             {'name':'error','type':'integer'},
	             {'name':'date_t','type':'text'},
	             {'name':'date_u','type':'integer'},
	             {'name':'a_date_t','type':'text'},
	             {'name':'a_date_u','type':'integer'}]
	        }

	def __init__(self, nameDB, fileCSV ):
		self.ENDPOINT = 0x00
		self.TIME = 0x0F
		self.KEEP_ALIVE = 0x21 
		self.ALARM = 0x55
		self.ALARM_ON = 0x56
		self.FINISH = 0xAA
		self.ERROR = 0xFF
		self.OTHER = 0x01
		self.nameDB = nameDB
		self.fileCSV = fileCSV
		#self.cursor_ACM = self.conn.cursor()
		if not(os.path.isfile(nameDB)):
			conn = sqlite3.connect(self.nameDB,timeout=30)
			self.prepare(conn)
			self.csv_bulk()
			conn.close()
		else:
			conn = sqlite3.connect(self.nameDB,timeout=30)
			conn.close()

	def prepare(self,conn):
		cursor_ACM = conn.cursor()
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS endpoint(id INTEGER PRIMARY KEY, code TEXT, type TEXT, dest_high TEXT, dest_low TEXT)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS time(id INTEGER PRIMARY KEY, code TEXT, date_t TEXT, date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS alarm(id INTEGER PRIMARY KEY, code TEXT, date_t TEXT, date_u INTEGER, a_date_t TEXT, a_date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS alarm_on(id INTEGER PRIMARY KEY, code TEXT, name TEXT, scan INTEGER,date_t TEXT, date_u INTEGER, a_date_t TEXT, a_date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS keep_alive(id INTEGER PRIMARY KEY, code TEXT,date_t TEXT, date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS finish(code TEXT,date_t TEXT, date_u INTEGER, a_date_t TEXT, a_date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS error(code TEXT, errc INTEGER, date_t TEXT, date_u INTEGER, a_date_t TEXT, a_date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS other(id INTEGER PRIMARY KEY, code TEXT, err INTEGER, date_t TEXT, date_u INTEGER)''')
		conn.commit()

	def csv_bulk(self):
		with open(self.fileCSV,'r') as f:
				reader = csv.reader(f)
				for row in reader:
					row_d = dict(zip(('code','type','dest_high','dest_low'),row))
					self.insert(self.ENDPOINT,**row_d)


	def insert(self, tag, **args ):
		conn = sqlite3.connect(self.nameDB,timeout=10)
		cursor_ACM = conn.cursor()
		if tag ==  self.ENDPOINT:
			if len(args) == 4:
				cursor_ACM.execute('''INSERT INTO endpoint VALUES (null,?,?,?,?)''',(args['code'],args['type'],args['dest_high'],args['dest_low']))
			else:
				print "Error INSERT " + str(self.ENDPOINT)
		elif tag == self.TIME:
			if len(args) == 3:
				cursor_ACM.execute('''INSERT INTO time VALUES (null,?,?,?)''',(args['code'],args['date_t'],args['date_u']))
			else:
				print "Error INSERT " + str(self.TIME)
		elif tag == self.KEEP_ALIVE:
			if len(args) == 3:
				cursor_ACM.execute('INSERT INTO keep_alive VALUES (null,?,?,?)',(args["code"],args["date_t"],args["date_u"]))
			else:
				print "Error INSERT " + str(self.KEEP_ALIVE)
		elif tag == self.ALARM:
			if len(args) == 5:
				cursor_ACM.execute('INSERT INTO alarm VALUES (null,?,?,?,?,?)',(args["code"],args["date_t"],args["date_u"],args["a_date_t"],args["a_date_u"]))
			else:
				print "Error INSERT " + str(self.ALARM)
		elif tag == self.ALARM_ON:
			if len(args) == 7:
				cursor_ACM.execute('INSERT INTO alarm_on VALUES (null,?,?,?,?,?,?,?)',(args["code"],args["name"],args["scan"],args["date_t"],args["date_u"],args["a_date_t"],args["a_date_u"]))
			else:
				print "Error INSERT " + str(self.ALARM_ON)
		elif tag == self.FINISH:
			if len(args) == 5:
				cursor_ACM.execute('INSERT INTO finish VALUES (?,?,?,?,?)',(args["code"],args["date_t"],args["date_u"],args["a_date_t"],args["a_date_u"]))
			else:
				print "Error INSERT " + str(self.FINISH)
		elif tag == self.ERROR:
			if len(args) == 6:
				cursor_ACM.execute('INSERT INTO error VALUES (?,?,?,?,?,?)',(args["code"],args["errc"],args["date_t"],args["date_u"],args["a_date_t"],args["a_date_u"]))
			else:
				print "Error INSERT " + str(self.ERROR)
		elif tag == self.OTHER:
			if len(args) == 4:
				cursor_ACM.execute('INSERT INTO other VALUES (null,?,?,?,?)',(args["code"],args["err"],args["date_t"],args["date_u"]))
			else:
				print "Error INSERT " + str(self.OTHER)
		else:
			print "ERROR"

		conn.commit()
		conn.close()

	def _make_select_query(self,tag,cond):
		query = 'SELECT * FROM '
		query += self.table_name[tag]
		if cond != '':
			query += ' WHERE ' 
			query += cond
		return query 

	def select(self, tag, where=''):
		conn = sqlite3.connect(self.nameDB,timeout=10)
		cursor_ACM = conn.cursor()
		try:
			cursor_ACM.execute(self._make_select_query(tag,where))
			response =  cursor_ACM.fetchall()
		except:
			pass
		conn.close()
		return response

	def check(self):
		return os.path.isfile(self.nameDB)