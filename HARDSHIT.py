#!/usr/bin/python
import RPi.GPIO as GPIO
import argparse
import SHITDB
import time
import threading
import json

GPIO.setmode(GPIO.BCM)
aSHITType = {}
newPressAllowed = True
newPressTimer = None
# debounceTimeout = 0
# testAlertLength = 0

def debouncer():
	global newPressAllowed
	newPressAllowed = True

def startASHIT(shitType):
	print("Enabled alarm type %s" % shitType)
	if shitType == '2' or shitType == '1':
		print('2 high')
		GPIO.output(2, GPIO.HIGH)
	if shitType == '3' or shitType == '1':
		print('3 high')
		GPIO.output(3, GPIO.HIGH)

def stopASHIT(shitNo, dbConn):
	print("Disabled alarm")
	GPIO.output(2, GPIO.LOW)
	GPIO.output(3, GPIO.LOW)
	dbConn.finishASHIT(shitNo)


def main():
	# global debounceTimeout
	# global testAlertLength
	latestSHITLength = 0
	# setup pins as input
	GPIO.setup(list(map(int, aSHITType.keys())), GPIO.IN, pull_up_down=GPIO.PUD_UP)
	# setup pins as output
	GPIO.setup([2, 3], GPIO.OUT)
	
	# create database handaler.
	db = SHITDB.SHITdb(args.databaseHost, args.databaseName, args.databaseUsername, 
					args.databasePassword)
	
	# check if configs are overridden, if not set configs
	configData = db.getConfigData()
	debounceTimeout = configData[0]
	testAlertLength = configData[1]
	
	print(db.selectASpecficSHIT(1))
	# setup timer on the test alert so we have a dead timer object going forward also serves as a test of the alarm system.
	shit_no, shit_type, shit_time, shit_length, shit_finished = db.selectASpecficSHIT(1)[0]
	latestSHITLength = shit_length
	aCurrentSHIT = threading.Timer(1, stopASHIT, args=(shit_no, db))
	startASHIT(shit_type)
	aCurrentSHIT.start()
	latestSHITStartTime  = int(time.time())
	if args.lastAlarmNumber > 0:
		latestSHITNo = args.lastAlarmNumber
	else:
		latestSHITNo = db.selectPreviousASHIT()[0][0]

	def shitInterrupt(channel):
		global newPressAllowed
		global newPressTimer
		if newPressAllowed:
			newPressAllowed = False
			newPressTimer = threading.Timer(debounceTimeout, debouncer)
			newPressTimer.start()
			if aSHITType[str(channel)] == '4':
				db.insertASHIT('2', 2)
				db.insertASHIT('3', 2)
				db.insertASHIT('1', 2)
			else:
				db.insertASHIT(aSHITType[str(channel)], testAlertLength)
	
	# assing intrrupt to pins
	for pin in map(int, aSHITType.keys()):
		GPIO.add_event_detect(pin, GPIO.RISING, callback=shitInterrupt)
	
	try:
		while True:
			configData = db.getConfigData()
			debounceTimeout = configData[0]
			testAlertLength = configData[1]
			for shit_no, shit_type, shit_time, shit_length, shit_finished in db.selectAllASHIT():
				# If this is a new alarm (or at least more recent than the current one)
				if shit_no > latestSHITNo:
					print(shit_no, shit_length, shit_type)
					# Legacy code that uses the old method for canceling an alarm
					if shit_type == 5:
						if aCurrentSHIT.is_alive():
							aCurrentSHIT.cancel()
							stopASHIT(shit_no, db)
							latestSHITNo = shit_no
					# Starts new alarms
					elif not aCurrentSHIT.is_alive():
						if not shit_finished:
							print("starting shit")
							startASHIT(shit_type)
							aCurrentSHIT = threading.Timer(float(shit_length), stopASHIT, args=(shit_no, db))
							aCurrentSHIT.start()
							latestSHITNo = shit_no
							latestSHITLength = int(shit_length)
							latestSHITStartTime = int(time.time())
				# Handel changes to the curent alarm 
				elif shit_no == latestSHITNo:
					print("Same shit")
					# End the alram early if it is manually set
					if shit_finished == 1:
						if aCurrentSHIT.is_alive():
							print("canceling shit")
							aCurrentSHIT.cancel()
							stopASHIT(shit_no, db)
					# Change the length of the current alarm
					elif latestSHITLength != shit_length:
						print("modifying shit time")
						aCurrentSHIT.cancel()
						aCurrentSHIT = threading.Timer(float(abs(shit_length - int(latestSHITStartTime - int(time.time())))), stopASHIT)
				# Handel alarms manually marked as unfinished
				if not shit_finished:
					if not aCurrentSHIT.is_alive():
						startASHIT(shit_type)
						aCurrentSHIT = threading.Timer(float(shit_length), stopASHIT, args=(shit_no, db))
						aCurrentSHIT.start()
						latestSHITNo = shit_no
						latestSHITLength = int(shit_length)
						latestSHITStartTime = int(time.time())

			time.sleep(1)
			print("new press allowed: %s" % str(newPressAllowed))
			print(newPressTimer)

	except KeyboardInterrupt:
		pass
	finally:
		GPIO.cleanup()		

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="Hardware Action Reporting Device for Secure Heart Information Transmitter.")
	parser.add_argument("-N", "--databaseName", type=str, help="Name of the database used by the Secure Heart Information Transmitter. Default is doshit", default="doshit")
	parser.add_argument("-H", "--databaseHost", type=str, help="The host the database is running on.  Default is 127.0.0.1", default="127.0.0.1")
	parser.add_argument("-U", "--databaseUsername", type=str, help="Username to be used for the database connection. Default is dashit", default="dashit")
	parser.add_argument("-P", "--databasePassword", type=str, help="Password to be used for the database connection. Default is Password1!", default="Password1!")
	parser.add_argument("-a", "--lastAlarmNumber", type=int, help="The set the inital value for the last alarm", default = -1)
	parser.add_argument('-p', '--pinMap', type=lambda x: json.load(open(x)), help="Specifiy the pin mapping file for pin to alarm mapping. Default filename is pinMap.json", default=json.load(open('pinMap.json')))
	args = parser.parse_args()
	aSHITType = args.pinMap
	main()
