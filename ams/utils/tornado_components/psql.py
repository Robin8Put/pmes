import psycopg2
from psycopg2 import sql


class DBResult(object):
	"""Tool for returning result of database work
	"""
	codes = {
		0: True
		1: "Database opened",
		2: "Database closed",
		3: "Created/Updated",
		4: "Denied",
		5: "Error"
	}

	def __new__(self, code, reason=None):
		if reason:
			return {code: reason}
		else: 
			return {code:self.codes[code]}



class Table(object):
	"""Driver for postgresql interacting
	"""
	def __init__(self,table,dbname,user,host,password):

		self.dbname = dbname
		self.user = user
		self.host = host
		self.password = password 

		# Set database connection
		self.conn = psycopg2.connect(dbname=self.dbname, user=self.user,
									host=self.host, password=self.password)
		# Set interacting with database cursor
		self.cursor = self.conn.cursor()
		# Set table name
		self.table = table

	

	def close(self):
		"""Close database connection
		"""
		self.cursor.close()
		self.conn.close()
		return DBResult(2)


	def open(self):
		"""Open database connection
		"""
		# Set database connection
		self.conn = psycopg2.connect(dbname=self.dbname, user=self.user,
									host=self.host, password=self.password)
		# Set interacting with database cursor
		self.cursor = self.conn.cursor()
		return DBResult(1)


	def insert(self, **kwargs):
		"""Write data to database table.
		Accepts field names and values.
		Returns success or error.

		Raises exception if required fields missed.

		Based on posibility to pass arbitrary amount of parameters.

		insert(**kwargs) => {1: 'Success'}
		insert(**kwargs) => {3: 'Error text'}
		"""
		# Set field names and values for inserting
		keys, values = list(kwargs.keys()), list(kwargs.values())

		try:
			# Build sql query for all passed parameters
			query = sql.SQL("INSERT INTO {} ({}) values ({})").format(
							# table name
							sql.Identifier(self.table),
							# field names
							sql.SQL(', ').join(map(sql.Identifier, keys)),
							# placeholders for values
							sql.SQL(', ').join(sql.Placeholder() * len(keys)))
			# Execute sql string with values
			self.cursor.execute(query, values)
			
			return DBResult(3)
		except Exception as e:
			return DBResult(5, str(e))


	def read(self, *_ids):
		"""Read data from database table.
		Accepts ids of entries.
		Returns list of results if success
			or string with error code and explanation.

		read(*id) => [(result), (result)] (if success)
		read(*id) => [] (if missed)
		read() => {5: "Missed required fields"}
		"""
		if not _ids:
			return DBResult(5, "Missed required fields")

		try:
			# Set sql string composition
			query = sql.SQL("SELECT * FROM {} where id in ({})").format(
							# table name
							sql.Identifier(self.table),
							# placeholders for values 
							sql.SQL(', ').join(sql.Placeholder() * len(_ids)))
			# Execute sql strinf with values
			self.cursor.execute(query, _ids)
			return self.cursor.fetchall()

		except Exception as e:
			return DBResult(5, str(e))


	def update(self, _id=None, **kwargs):
		"""Updates fields values.
		Accepts id of sigle entry and 
			fields with values.

		update(id, **kwargs) => {3: 'Created/Updated'} (if success)
		update(id, **kwargs) => {5: 'Error'} (if error)
		"""
		if not _id or not kwargs:
			return DBResult(5, "Missed required fields")

		for i in kwargs:
			try:
				query = sql.SQL("UPDATE {} SET {}={} WHERE id IN({})").format(
							sql.Identifier(self.table),
							sql.Identifier(i), sql.Literal(kwargs[i]),
							sql.SQL(', ').join(sql.Placeholder() * len((_id, ))))

				self.cursor.execute(query, (_id, ))
			except Exception as e:
				return DBResult(5, str(e))

		return DBResult(3)


	def find(self, key=None, *values):
		"""Find all entries with given search key.
		Accepts named parameter key and arbitrary values.
		Returns list of entry id`s.

		find(key, *values) => [id, id, id, id] (if exist)
		find(key, *values) => [] (if does not exist)
		find() => {5: "Missed required fields"}
		"""
		if not key or not values:
			return DBResult(5, "Missed required fields")
		try:
			# Set sql string composition
			query = sql.SQL("SELECT id FROM {} WHERE {} in ({})").format(
							# table name
							sql.Identifier(self.table),
							# search key name
							sql.Identifier(key),
							# placeholders 
							sql.SQL(', ').join(sql.Placeholder() * len(values)))
			# Execute sql string with values
			self.cursor.execute(query, values)
			return self.cursor.fetchall()

		except Exception as e:
			return DBResult(5, str(e))
		


	def delete(self, _id=None):
		"""Delete entry from database table.
		Accepts id.
		delete(id) => {0: True} (if exists)
		delete(id) => {5: 'Error'} (if does not exist)
		delete() => {5: 'Missed required fields'}
		"""
		if not _id:
			return DBResult(5, "Missed required fields")

		try:	
			# Set sql string composition
			query = sql.SQL("DELETE FROM {} WHERE id in ({})").format(
							# table name
							sql.Identifier(self.table),
							# placeholder for values
							sql.Placeholder())
			# Execute deleting
			self.cursor.execute(query, (_id,))
			return DBResult(0)

		except Exception as e:
			return DBResult(5, str(e))


	def save(self):
		# Commit changes to database
		self.conn.commit()
		return DBResult(0)







