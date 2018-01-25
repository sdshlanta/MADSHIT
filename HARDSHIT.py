import RPi.GPIO as GPIO
import argparse
import mysql.connector
import time
import threading
import json

GPIO.setmode(GPIO.BCM)

aCurrentSHIT = None
aSHITType = {}

def startASHIT():
	print("Enabled alarm")
	GPIO.output(2, GPIO.HIGH)
	GPIO.output(3, GPIO.HIGH)

def stopASHIT():
	global aCurrentShit
	print("Disabled alarm")
	GPIO.output(2, GPIO.LOW)
	GPIO.output(3, GPIO.LOW)
	aCurrentSHIT = None

def main():

	latestSHITNo = args.lastAlarmNumber

	def shitInterrupt(channel):
		
		insertionQuery = "INSERT INTO ashit (shit_type, shit_length) VALUES (%s, %d)"
		data = (aSHITType[str(channel)], args.testAlertLength)
		dbConn = mysql.connector.connect(user=args.databaseUsername, password=args.databasePassword,
											host=args.databaseHost,
											database=args.databaseName)
		cur = dbConn.cursor()
		print(insertionQuery % data)
		cur.execute(insertionQuery % data)
		dbConn.commit()
		
		print(cur.lastrowid)
		cur.execute('SELECT * FROM ashit ORDER BY shit_time DESC LIMIT 1')
		for row in cur:
			print(row)
		
		cur.close()
		dbConn.close()
	
	GPIO.setup(list(map(int, aSHITType.keys())), GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup([2, 3], GPIO.OUT)

	for pin in map(int, aSHITType.keys()):
		GPIO.add_event_detect(pin, GPIO.RISING, callback=shitInterrupt)
	
	try:
		while True:
			dbConn = mysql.connector.connect(user=args.databaseUsername, password=args.databasePassword,
											host=args.databaseHost,
											database=args.databaseName)
			cur = dbConn.cursor()
			cur.execute("SELECT shit_no, shit_length, shit_type FROM ashit ORDER BY shit_time DESC LIMIT 1")
			for shit_no, shit_length, shit_type in cur:
				if shit_no > latestSHITNo:
					print(shit_no, shit_length, shit_type)
					if shit_type == 5:
						if aCurrentSHIT is not None:
							aCurrentSHIT.cancel()
							stopASHIT()
							latestSHITNo = shit_no

					elif aCurrentSHIT is None:
						latestSHITNo = shit_no
						startASHIT()
						global aCurrentSHIT
						aCurrentSHIT = threading.Timer(float(shit_length), stopASHIT)
						aCurrentSHIT.start()
			
			print(aCurrentSHIT)
			import code
			code.interact(local=locals())
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
	finally:
		GPIO.cleanup()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Hardware Action Reporting Device for Secure Heart Information Transmitter.")
	parser.add_argument("-N", "--databaseName", type=str, help="Name of the database used by the Secure Heart Information Transmitter. Default is 'doshit'.", default="doshit")
	parser.add_argument("-H", "--databaseHost", type=str, help="The host the database is running on.  Default is 127.0.0.1", default="127.0.0.1")
	parser.add_argument("-U", "--databaseUsername", type=str, help="Username to be used for the database connection. Default is root", default="daSHIT")
	parser.add_argument("-P", "--databasePassword", type=str, help="Password to be used for the database connection. Default is blank", default="")
	parser.add_argument("-l", "--testAlertLength", type=int, help="The amount of time a test alert should last", default=5)
	parser.add_argument("-a", "--lastAlarmNumber", type=int, help="The set the inital value for the last alarm", default = -1)
	parser.add_argument('-p', '--pinMap', type=lambda x: json.load(open(x)), help="Specifiy the pin mapping file for pin to alarm mapping. Default filename is pinMap.json", default=json.load(open('pinMap.json')))
	args = parser.parse_args()
	aSHITType = args.pinMap
	main()
