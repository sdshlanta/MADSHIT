import time
import mysql.connector

class SHITdb(object):
	def __init__(self, host, database, username, password):
		self.host = host
		self.database = database
		self.username = username
		self.password = password
	
	def _getDatabaseConnection(self, retries=10):
		for x in range(retries):
			try:
				dbConn = mysql.connector.connect(user=self.username, password=self.password,
												host=self.host,
												database=self.database)
				break
			except mysql.connector.errors.InterfaceError:
				time.sleep(1)
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
		insertionQuery = "INSERT INTO users (user_name, user_passwd, user_type) VALUES ('%s', '%s', %s)"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(insertionQuery % (username, password, userType))
		dbConn.commit()
		cur.close()
		dbConn.close()
	
	def selectUser(self, username):
		selectQuery = "SELECT * FROM users WHERE user_name = '%s'"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(selectQuery % username)
		rows = [row for row in cur]
		cur.close()
		dbConn.close()
		return rows

	def selectAllUsers(self):
		selectQuery = "SELECT * FROM users"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(selectQuery)
		rows = [row for row in cur]
		cur.close()
		dbConn.close()
		return rows
	
	def updateUser(self, userNo, username, password, userType):
		updateQuery = "UPDATE users SET user_name='%s', user_passwd='%s', user_type='%s' WHERE user_no = '%s'"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(updateQuery % (username, password, userType, userNo))
		dbConn.commit()
		cur.close()
		dbConn.close()

	def selectPreviousASHIT(self, limit = 1):
		selectQuery = "SELECT shit_no, shit_length, shit_type, shit_finished FROM ashit ORDER BY shit_time DESC LIMIT %d"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(selectQuery % limit)
		rows = [row for row in cur]
		cur.close()
		dbConn.close()
		return rows
	
	def selectAllASHIT(self):
		selectQuery = "SELECT * FROM ashit"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(selectQuery)
		rows = [row for row in cur]
		cur.close()
		dbConn.close()
		return rows		

	def selectASpecficSHIT(self, shit_no):
		selectQuery = "SELECT * FROM ashit WHERE shit_no = '%s';"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(selectQuery % str(shit_no))
		rows = [row for row in cur]
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
		selectQuery = "SELECT user_no FROM users WHERE user_type = 1 AND user_name = '%s'"
		dbconn = self._getDatabaseConnection()
		cur = dbconn.cursor()
		cur.execute(selectQuery % username)
		rows = [row for row in cur]
		cur.close()
		dbconn.close()
		return rows

	def updateASHIT(self, shit_no, shit_type, shit_time, shit_length, shit_finished):
		updateQuery = "UPDATE ashit SET shit_type='%s', shit_time='%s', shit_length='%s', shit_finished='%s' WHERE shit_no = '%s'"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(updateQuery % (shit_type, shit_time, shit_length, shit_finished, shit_no))
		dbConn.commit()
		cur.close()
		dbConn.close()
	
	def finishASHIT(self, shit_no):
		updateQuery = "UPDATE ashit SET shit_finished='1' WHERE shit_no = '%s'"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(updateQuery %  shit_no)
		dbConn.commit()
		cur.close()
		dbConn.close()
	
	def getConfigData(self):
		selectQuery = "SELECT * FROM SHITconfig"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(selectQuery)
		rows = [row for row in cur]
		cur.close()
		dbConn.close()
		return rows[0]
	
	def updateConfig(self, debouce_timeout, alarm_length, wireless_ssid, wireless_password, wireless_encryption):
		updateQuery = "UPDATE SHITconfig SET debounce_timeout='%s', alarm_length='%s', wireless_ssid='%s', wireless_password='%s', wireless_encryption='%s'"
		dbConn = self._getDatabaseConnection()
		cur = dbConn.cursor()
		cur.execute(updateQuery % (debouce_timeout, alarm_length, wireless_ssid, wireless_password, wireless_encryption))
		dbConn.commit()
		cur.close()
		dbConn.close()