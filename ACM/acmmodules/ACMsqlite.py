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

	"""
	Name: __init__

	Set the Flags, and create and populate the SQLite3
	Database if not exists, calling _prepare and _csv_bulk
	"""
	def __init__(self, nameDB, fileCSV ):
		self.ENDPOINT   = 0x00
		self.TIME       = 0x0F
		self.KEEP_ALIVE = 0x21 
		self.ALARM      = 0x55
		self.ALARM_ON   = 0x56
		self.FINISH     = 0xAA
		self.ERROR      = 0xFF
		self.OTHER      = 0x01
		self.nameDB = nameDB
		self.fileCSV = fileCSV

		if not(os.path.isfile(nameDB)):
			conn = sqlite3.connect(self.nameDB,timeout=10)
			self._prepare(conn)
			self._csv_bulk()
			conn.close()

	"""
	Name: _prepare(conn)
	conn: Connection to the SQLite3 Database

	Create the Tables for the ACM Database
	"""
	def _prepare(self,conn):
		cursor_ACM = conn.cursor()
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS endpoint(id INTEGER PRIMARY KEY, code TEXT, type TEXT, dest_high TEXT, dest_low TEXT)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS time(id INTEGER PRIMARY KEY, code TEXT, date_t TEXT, date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS alarm(id INTEGER PRIMARY KEY, code TEXT, date_t TEXT, date_u INTEGER, a_date_t TEXT, a_date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS alarm_on(id INTEGER PRIMARY KEY, code TEXT, name TEXT, scan INTEGER,date_t TEXT, date_u INTEGER, a_date_t TEXT, a_date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS keep_alive(id INTEGER PRIMARY KEY, code TEXT,date_t TEXT, date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS finish(id INTEGER PRIMARY KEY,code TEXT,date_t TEXT, date_u INTEGER, a_date_t TEXT, a_date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS error(id INTEGER PRIMARY KEY,code TEXT, errc INTEGER, date_t TEXT, date_u INTEGER, a_date_t TEXT, a_date_u INTEGER)''')
		cursor_ACM.execute('''CREATE TABLE IF NOT EXISTS other(id INTEGER PRIMARY KEY, code TEXT, err INTEGER, date_t TEXT, date_u INTEGER)''')
		conn.commit()

	"""
	Name: _csv_bulk

	Read the CSV File, with the data of the Endpoint,
	and insert it the Database
	"""
	def _csv_bulk(self):
		with open(self.fileCSV,'r') as f:
				reader = csv.reader(f)
				for row in reader:
					row_d = dict(zip(('code','type','dest_high','dest_low'),row))
					self.insert(self.ENDPOINT,**row_d)

	"""
	Name: _make_delete_query

	tag: TAG of the Table
	where: Where Statement

	Make the Query to delete the selected columns

	return: DELETE query 
	"""
	def _make_delete_query(self,tag,where):
		return 'DELETE FROM ' + self.table_name[tag] + (' WHERE ' + where if where != '' else where)
	

	"""
	Name: _make_select_query

	tag: TAG of the Table
	fields: Fields of the Table
	where: Where Statement
	limit: limit of results

	Make the Query to select columns

	return: SELECT query 
	"""
	def _make_select_query(self,tag,fields='*',where='',limit=0):
		query = 'SELECT '
		query += fields + ' FROM '
		query += self.table_name[tag]
		if where != '':
			query += ' WHERE ' + where 
		if limit != 0:
			query += 'LIMIT ' + str(limit)
		return query 

	def _insert_bulk(self,tag, **args):
		conn = sqlite3.connect(self.nameDB,timeout=30)
		cursor_ACM = conn.cursor()
		try:
			#TODO
			cursor_ACM.executemany()
			conn.commit()
		except Exception, e:
			raise ValueError(e,'Error insert bulk data')
		finally:
			conn.close()
	"""
	Name: insert

	tag: TAG of Table
	args: dictionary of the elements of the Table

	Insert a row in the specific table
	"""
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
				cursor_ACM.execute('INSERT INTO finish VALUES (null,?,?,?,?,?)',(args["code"],args["date_t"],args["date_u"],args["a_date_t"],args["a_date_u"]))
			else:
				print "Error INSERT " + str(self.FINISH)
		elif tag == self.ERROR:
			if len(args) == 6:
				cursor_ACM.execute('INSERT INTO error VALUES (null,?,?,?,?,?,?)',(args["code"],args["errc"],args["date_t"],args["date_u"],args["a_date_t"],args["a_date_u"]))
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
	
	"""
	Name: insert

	tag: TAG of Table
	fields: Table Fields (string)
	where: where statement
	fetch_one: if fetch_one=True, only return 1 result

	Select data form database

	return data
	"""

	def select(self, tag, fields ='', where='',fetch_one=False):
		conn = sqlite3.connect(self.nameDB,timeout=10)
		cursor_ACM = conn.cursor()
		try:
			cursor_ACM.execute(self._make_select_query(tag,fields,where))
			if fetch_one:
				data = cursor_ACM.fetchone()
			else:
				data = cursor_ACM.fetchall()
		except Exception, e:
			raise ValueError(e)
		finally:
			conn.close()
		return data

	"""
	Name: is_empty

	tag: TAG of Table

	Check if a Table is empty

	Return: 0 if empty, 
			# of rows if not empty
	"""
	def is_empty(self,tag):
		conn = sqlite3.connect(self.nameDB,timeout=10)
		cursor_ACM = conn.cursor()
		try:
			cursor_ACM.execute(self._make_select_query(tag,fields='count(*)'))
			data = cursor_ACM.fetchone()
			value = 0 if data[0] == 0 else data[0]
		except Exception, e:
			raise ValueError(e)
		finally:
			conn.close()
		return value
	"""
	Name: delete

	tag: TAG of Table
	where: where statement

	Delete if a Table

	Return: # of rows deleted
	"""
	def delete(self,tag,where):
		conn = sqlite3.connect(self.nameDB,timeout=30)
		cursor_ACM = conn.cursor()
		try:
			data = cursor_ACM.execute(self._make_delete_query(tag,where)).rowcount
		except Exception, e:
			raise ValueError(e)
		finally:
			conn.commit()
			conn.close()
		return data

		"""
	Name: check
	
	Check if Database Exist
	Return: True if exist, False if not
	"""
	def check(self):
		return os.path.isfile(self.nameDB)