import sqlite3
import RPi.GPIO as GPIO
import argparse
import mysql.connector
import time
from datetime import datetime


GPIO.setmode(GPIO.BCM)

channelMap = {
	1:1,
	2:2,
	3:3,
	4:4
}


def main():
	def shitInterrupt(channel):
		timeOfSHIT = datetime.now()
		insertionQuery = "INSERT INTO ashit (shit_type, shit_time, shit_length) VALUES (%d, %s, %d)"
		data = (channelMap[channel], timeOfSHIT, args.testAlertLength)
		dbConn = mysql.connector.connect(user=args.databaseUsername, password=args.databasePassword,
									host=args.databaseHost,
									database=args.databaseName)
		cur = dbConn.cursor()
		cur.execute(insertionQuery, data)
		cur.close()
		dbConn.close()
	GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(2, GPIO.RISING, callback=shitInterrupt)
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		GPIO.cleanup()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Hardware Action Reporting Device for Secure Heart Information Transmitter.")
	parser.add_argument("-N", "--databaseName", type=str, help="Name of the database used by the SHIT. Default is 'doshit'.", default="doshit")
	parser.add_argument("-H", "--databaseHost", type=str, help="The host the database is running on.  Default is 127.0.0.1", default="127.0.0.1")
	parser.add_argument("-U", "--databaseUsername", type=str, help="Username to be used for the database connection. Default is root", default="root")
	parser.add_argument("-P", "--databasePassword", type=str, help="Password to be used for the database connection. Default is Password1!", default="Password1!")
	parser.add_argument("-l", "--testAlertLength", type=int, help="The amount of time a test alert should last", default=5)
	args = parser.parse_args()
	main()