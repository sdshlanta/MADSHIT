#!/usr/bin/python
from flask import Flask, render_template, session, request, redirect, url_for
from logging.handlers import RotatingFileHandler
from time import strftime
import SHITDB
import argparse
import os
import logging
import traceback

app = Flask("Alarm Database Interface Connector")

def constructError(error, returnLocation):
	session['error'] = error
	session['returnURL'] = url_for(returnLocation)
	return redirect(url_for('error'))

def constructSuccess(success, returnLocation):
	session['success'] = success
	session['returnURL'] = url_for(returnLocation)
	return redirect(url_for('success'))

def readKey(path):
	if "This is some mad SHIT!?!" == path:
		return path
	try:
		with open(path, 'r') as fp:
			key = fp.read()
		return key
	except IOError:
		logger.warning('Unable to access key file at "%s", using default key instead.', path)
		return "This is some mad SHIT!?!"

@app.route('/',methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		matchingUser = db.checkUserCreds(request.form['username'], request.form['password'])
		if matchingUser:
			session['username'] = request.form['username']
			session['logged_in'] = True
			username = session['username']			
			if matchingUser[0][1]:
				session['admin'] = True
		else:
			session['error'] = 'Incorrect username or password.'
			session['returnURL'] = url_for('index')
			return redirect(url_for('error'))
	else:
		if 'username' in session:
			session['logged_in'] = True
			username = session['username']
		else:
			username = None
	return render_template('index.html')

@app.route('/logout', methods=['GET'])
def logout():
	if 'logged_in' in session:
		del session['logged_in']
	if 'username' in session:
		del session['username']
	if 'admin' in session:
		del session['admin']
	return redirect(url_for('index'))

@app.route('/error', methods=['GET'])
def error():
	error = session['error']
	returnURL = session['returnURL']
	del session['error']
	del session['returnURL']
	return render_template('error.html', error=error, returnURL=returnURL)

@app.route('/success', methods=['GET'])
def success():
	success = session['success']
	returnURL = session['returnURL']
	del session['success']
	del session['returnURL']
	return render_template('success.html', success=success, returnURL=returnURL)

@app.route('/api/addUser', methods = ['POST'])
def addUser():
	if len(request.form['password']) != 8:
		return constructError('Password must be EXACTLY 8 chars.', 'renderAddUser')
	elif db.checkForExistingUser(request.form['username']):
		return constructError('Username already taken.', 'renderAddUser')
	try:
		db.insertUser(
			request.form['username']
			,request.form['password']
			,int(request.form['isAdmin'] == 'admin')
		)
		return constructSuccess('User %s created!'% request.form['username'], 'renderAddUser' )
	except Exception as e:
		return constructError('Unable to add %s, the following error occured: %s' % (request.form['username'], str(e)), 'renderAddUser')

@app.route('/addUser', methods = ['GET'])
def renderAddUser():
	if 'logged_in' not in session:
		return redirect(url_for('index'))
	else:
		return render_template('addUser.html')

@app.route('/u/<username>', methods = ['GET'])
def renderUserInfo(username):
	rows = db.selectUser(username)
	if not rows:
		return constructError('Unable to find user %s' % username, 'index')
	else:
		userNo, username, password, isAdmin = rows[0]
		if 'username' in session:
			if 'admin' in session or (session['username'] == username):
				return render_template('userInfo.html', userNo = userNo, username=username, password=password, isAdmin=isAdmin )			
		return render_template('userInfo.html', userNo = userNo, username=username, isAdmin=isAdmin )


@app.route('/users', methods = ['GET'])
def renderUserList():
	if 'logged_in' not in session:
		return redirect(url_for('index'))
	else:
		rows = db.selectAllUsers()
		return render_template('userList.html', rows = rows)

@app.route('/api/updateUser', methods = ['POST'])
def updateUser():
	form = request.form
	if len(form['password']) != 8:
		return constructError('Password must be EXACTLY 8 chars.', 'renderUserList')
	try:
		db.updateUser(
			form['userNo']
			,form['username']
			,form['password']			
			,form['isAdmin']
		)
		return constructSuccess('Updated user %s, please logout and login for chagnes to take place.' % form['username'], 'renderUserList')
	except Exception as e:
		return constructError('Unable to update user %s the followig error occurred: %s' % (form['username'],str(e)), 'renderUserList')
	

@app.route('/checkAlarms', methods = ['GET'])
def renderASHITCheck():
	if 'logged_in' not in session:
		return redirect(url_for('index'))
	else:
		rows = db.selectAllASHIT()
		return render_template('databaseInterface.html', rows=rows)

@app.route('/api/updateASHIT', methods = ['POST'])
def updateASHIT():
	form = request.form
	try:
		db.updateASHIT(
			form['shit_no']
			,form['shit_type']
			,form['shit_time']
			,form['shit_length']
			,form['shit_finished']
		)
		redir = constructSuccess('Alarm number %s updated' % form['shit_no'], 'renderASHITCheck')
	except Exception as e:
		redir = constructError('Update ot alarm number %s failed due to: %s' % (form['shit_no'], str(e)), 'renderASHITCheck' )
	finally:
		return redir

@app.route('/aSHIT/<shit_no>', methods=['GET'])
def renderDatabaseDetail(shit_no):
	if 'logged_in' not in session:
		return redirect(url_for('index'))
	else:
		no_shit, shit_type, shit_time, shit_length, shit_finished = db.selectASpecficSHIT(shit_no)[0]
		return render_template(
			'alarmDetail.html'
			,shit_no=no_shit
			,shit_type=shit_type
			,shit_time=shit_time
			,shit_length=shit_length
			,shit_finished=shit_finished
		)

@app.route('/config/alarms', methods=['GET'])
def renderConfigAlarms():
	if 'logged_in' not in session:
		return redirect(url_for('index'))
	else:
		debounce_timeout, alarm_length, session['wireless_ssid'], session['wireless_password'], session['wireless_encryption']= db.getConfigData()
		return render_template(
			'configAlarms.html'
			,debounce_timeout = debounce_timeout
			,alarm_length = alarm_length
		)

@app.route('/api/config/alarms', methods=['POST'])
def configAlarms():
	form = request.form
	try:
		db.updateConfig(
			form['debounce_timeout']
			,form['alarm_length']
			,session['wireless_ssid']
			,session['wireless_password']
			,session['wireless_encryption']
		)
		redir = constructSuccess('Settings have been saved', 'renderConfigAlarms')
	except Exception as e:
		redir = constructError('Unable to save settings, failed due to: %s' % str(e), 'renderConfigAlarms' )
	finally:
		del session['wireless_ssid']
		del session['wireless_password']
		del session['wireless_encryption']
		return redir

@app.route('/config/wireless', methods=['GET'])
def renderConfigWireless():
	if 'logged_in' not in session:
		return redirect(url_for('index'))
	else:
		session['debounce_timeout'], session['alarm_length'],  wirelessSSID, wirelessPassword, wirelessEncryption = db.getConfigData()
		return render_template(
			'configWireless.html'
			,wirelessSSID = wirelessSSID
			,wirelessPassword = wirelessPassword
			,wirelessEncryption = wirelessEncryption
		)

@app.route('/api/config/wireless', methods=['POST'])
def configWireless():
	redir = None
	form = request.form
	try:
		if form['wirelessEncryption'] == 'WEP':
			command = "sudo bash -c \"echo '%s' > /etc/wpa_supplicant/wpa_supplicant.conf\""
			configString = '''ctrl_interface=/run/wpa_supplicant GROUP=netdev\n
			network={
				ssid=\\"%s\\"
				scan_ssid=1
				key_mgmt=NONE
				wep_tx_keyidx=0
				wep_key0=%s
			}'''
			commandToExecute = command % (configString % (form['wirelessSSID'], form['wirelessPassword']))
			os.system(commandToExecute)
			os.system('sudo pkill wpa_supplicant')
			os.system('sudo wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf')
		elif form['wirelessEncryption'] == 'WPA' or form['wirelessEncryption'] == 'WPA2':
			command = 'sudo bash -c "wpa_passphrase %s %s > /etc/wpa_supplicant/wpa_supplicant.conf"'
			updateConfig = command % (form['wirelessSSID'], form['wirelessPassword'])
			os.system('echo `whoami`')
			os.system(updateConfig)
			os.system('sudo pkill wpa_supplicant')
			os.system('sudo wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf')
		else:
			redir = constructError('Unknown encryption type', 'renderConfigWireless')
		if not redir:
			db.updateConfig(session['debounce_timeout'], session['alarm_length'],  form['wirelessSSID'], form['wirelessPassword'], form['wirelessEncryption'] )
			redir = constructSuccess('Settings have been saved', 'renderConfigWireless')
	except Exception as e:
		redir = constructError('Unable to save settings, failed due to: %s' % str(e), 'renderConfigWireless')
	finally:
		del session['debounce_timeout']
		del session['alarm_length']
	return redir

@app.after_request
def afterRequest(response):
	if response.status_code != 500:
		if request.form:
			data = request.form
		else:
			data = ''
		ts = strftime('[%Y-%b-%d %H:%M]')
		logger.info('%s %s %s %s %s %s %s',
			ts,
			request.remote_addr,
			request.method,
			request.scheme,
			request.url,
			response.status,
			data)
	return response

@app.errorhandler(Exception)
def logExceptions(e):
	ts = strftime('[%Y-%b-%d %H:%M]')
	tb = traceback.format_exc()
	logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
		ts,
		request.remote_addr,
		request.method,
		request.scheme,
		request.url,
		tb)
	return "Internal Server Error", 500

def main():

	app.secret_key = readKey(args.secretKey)
	app.run("0.0.0.0", 5000, True)	
	
if __name__ == '__main__':
	parser = argparse.ArgumentParser("Secure Heart Information Transmitter Alarm Database Interface Connector")
	parser.add_argument("-N", "--databaseName", type=str, help="Name of the database used by the Secure Heart Information Transmitter. Default is 'doshit'.", default="doshit")
	parser.add_argument("-H", "--databaseHost", type=str, help="The host the database is running on.  Default is 127.0.0.1", default="127.0.0.1")
	parser.add_argument("-U", "--databaseUsername", type=str, help="Username to be used for the database connection. Default is dashit", default="dashit")
	parser.add_argument("-P", "--databasePassword", type=str, help="Password to be used for the database connection. Default is blank", default="Password1!")
	parser.add_argument("-L", "--logFile", type=str, help="The path to a file were you would like output logged.  By default a new log file will be created once the first reaches 100kB.  Default is SHITADIC.log", default="SHITADIC.log") 
	parser.add_argument("-S", "--logSize", type=int, help="The maximum size of the log file in bytes.  If this is set to 0 all data will be logged to the same file  Default is 100000", default=100000)
	parser.add_argument("-B", "--logBackups", type=int, help="The maximum number of old log files to to keep.  Default is 5", default=5)
	parser.add_argument("-s", "--secretKey", type=str, help="Path to file containing 24 random bytes to be used as the secret key", default="This is some mad SHIT!?!")
	args = parser.parse_args()
	db = SHITDB.SHITdb(args.databaseHost, args.databaseName, args.databaseUsername, args.databasePassword )
		

	handler = RotatingFileHandler(args.logFile, maxBytes=args.logSize, backupCount=args.logBackups)
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	logger.addHandler(handler)

	main()
	
