import sqlite3
import RPi.GPIO as GPIO
import argparse
import mysql.connector
import time
import threading
from datetime import datetime

aCurrentSHIT = None
GPIO.setmode(GPIO.BOARD)

aSHITType = {
	5:1,
	6:2,
	13:3,
	19:4
}

def enableAlarm():
	print("Enabled alarm")
	GPIO.output(2, GPIO.HIGH)
	GPIO.output(3, GPIO.HIGH)

def disableAlarm():
	print("Disabled alarm")
	GPIO.output(2, GPIO.HIGH)
	GPIO.output(3, GPIO.HIGH)
	aCurrentSHIT = None


def main():
	latestSHITNo = args.lastAlarmNumber

	def shitInterrupt(channel):
		insertionQuery = "INSERT INTO ashit (shit_type, shit_length) VALUES (%d, %d)"
		data = (aSHITType[channel], args.testAlertLength)
		
		cur = dbConn.cursor()
		# print(insertionQuery % data)
		cur.execute(insertionQuery % data)
		dbConn.commit()
		# print(cur.lastrowid)
		# cur.execute('SELECT * FROM ashit')
		# for row in cur:
		# 	print(row)
		
		cur.close()
		dbConn.close()
	
	GPIO.setup([5, 6, 13, 16], GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup([3, 4], GPIO.OUT)

	GPIO.add_event_detect(5, GPIO.RISING, callback=shitInterrupt)
	GPIO.add_event_detect(6, GPIO.RISING, callback=shitInterrupt)
	GPIO.add_event_detect(13, GPIO.RISING, callback=shitInterrupt)
	GPIO.add_event_detect(16, GPIO.RISING, callback=shitInterrupt)
	
	try:
		while True:
			dbConn = mysql.connector.connect(user=args.databaseUsername, password=args.databasePassword,
											host=args.databaseHost,
											database=args.databaseName)
			cur = dbConn.cursor()
			cur.execute("SELECT shit_no, shit_length, shit_type FROM ashit ORDER BY shit_time DESC LIMIT 1")
			for shit_no, shit_length, shit_type in cur:
				if shit_no > latestSHITNo:
					latestSHITNo = shit_no
					if shit_type == 5
						if aCurrentSHIT is not None:
							aCurrentSHIT.cancel()
							disableAlarm()
					elif aCurrentSHIT is None:
						enableAlarm()
						aCurrentSHIT = threading.Timer(shit_length, disableAlarm)
			cur.close()
			dbConn.close()
			time.sleep(1)
	except KeyboardInterrupt:
		try:
			cur.close()
		except:
			pass
		try:
			dbConn.close()
		except:
			pass
		GPIO.cleanup()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Hardware Action Reporting Device for Secure Heart Information Transmitter.")
	parser.add_argument("-N", "--databaseName", type=str, help="Name of the database used by the SHIT. Default is 'doshit'.", default="doshit")
	parser.add_argument("-H", "--databaseHost", type=str, help="The host the database is running on.  Default is 127.0.0.1", default="127.0.0.1")
	parser.add_argument("-U", "--databaseUsername", type=str, help="Username to be used for the database connection. Default is root", default="daSHIT")
	parser.add_argument("-P", "--databasePassword", type=str, help="Password to be used for the database connection. Default is blank", default="")
	parser.add_argument("-l", "--testAlertLength", type=int, help="The amount of time a test alert should last", default=5)
	parser.add_argument("-a", "--lastAlarmNumber", type=int, help="The set the inital value for the last alarm", default = -1)
	args = parser.parse_args()
	main()