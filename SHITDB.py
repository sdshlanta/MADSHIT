import mysql.connector

class SHITdb(object):
	def __init__(self, host, database, username, password):
		self.host = host
		self.database = database
		self.username = username
		self.password = password
	
	def _getDatabaseConnection(self):
		dbConn = mysql.connector.connect(user=self.username, password=self.password,
										host=self.host,
										database=self.database)
		return dbConn

	def insertASHIT(self, shit_type, shit_length, debug = False):
		insertionQuery = "INSERT INTO ashit (shit_type, shit_length) VALUES (%s, %d)"
		
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		
		if debug:
			print(insertionQuery % (shit_type, shit_length))
		
		cur.execute(insertionQuery % (shit_type, shit_length))
		dbConn.commit()
		
		if debug:
			print(cur.lastrowid)
			cur.execute('SELECT * FROM ashit ORDER BY shit_time DESC LIMIT 1')
			for row in cur:
				print(row)
		cur.close()
		dbConn.close()

	def insertUser(self, username, password, userType):
		insertionQuery = "INSERT INTO users (user_name, user_passwd, user_type) VALUES (%s, %s, %s)"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(insertionQuery % (username, password, userType))
		dbConn.commit()
		cur.close()
		dbConn.close()

	def selectMostRecentASHIT(self, limit = 1):
		selectQuery = "SELECT shit_no, shit_length, shit_type FROM ashit ORDER BY shit_time DESC LIMIT %d"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(selectQuery % limit)
		rows =  [row for row in cur]
		cur.close()
		dbConn.close()
		return rows

	def checkUserCreds(self, username, password):
		selectQuery = "SELECT user_no, user_type FROM users WHERE user_name = '%s' AND user_passwd = '%s'"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(selectQuery % (username, password))
		rows = [row for row in cur]
		cur.close()
		dbConn.close()
		return rows
	
	def checkForExistingUser(self, username):
		selectQuery = "SELECT user_no FROM users WHERE user_name = '%s'"
		dbconn = self._getDatabaseConnection()
		cur = dbconn.cursor()
		cur.execute(selectQuery % username)
		rows = [row for row in cur]
		print(rows)
		cur.close()
		dbconn.close()
		return rows
	
	def isAdmin(self, username):
		selectQuery = "SELECT user_no FROM users WHERE user_name = '%s' AND user_type = 1"
		dbconn = self._getDatabaseConnection()
		cur = dbconn.cursor()
		cur.execute(selectQuery % username)
		rows = [row for row in cur]
		cur.close()
		dbconn.close()
		return rows