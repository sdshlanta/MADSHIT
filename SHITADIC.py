from flask import Flask, render_template, session, request, redirect, url_for
import SHITDB
import argparse
import os

app = Flask("Alarm Database Interface Connector")

def constructError(error, returnLocation):
	session['error'] = error
	session['returnURL'] = url_for(returnLocation)
	return redirect(url_for('error'))

def constructSuccess(success, returnLocation):
	session['success'] = success
	session['returnURL'] = url_for(returnLocation)
	return redirect(url_for('success'))

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
		if 'admin' in session or (session['username'] == username):
			return render_template('userInfo.html', userNo = userNo, username=username, password=password, isAdmin=isAdmin )			
		else:
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
			command = "sudo bash -c 'iwconfig wlan0 essid %s key %s' &"
			# configString = '''country=GB
			# ctrl_interface=/var/run/wpa_supplicant
			# upddate_config=1
			# network={
			# 	ssid=%s
			# 	key_mgmt=NONE
			# 	wep_key0="%s
			# 	wep_tx_keyidx=0
			# }
			# '''
			commandToExecute = command % (form['wirelessSSID'], form['wirelessPassword'])
			os.system(commandToExecute)
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

def main():
	app.secret_key = "This is some mad SHIT!?!"
	app.run("0.0.0.0", 5000, True)
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser("Secure Heart Information Transmitter Alternitive Data Connector")
	parser.add_argument("-N", "--databaseName", type=str, help="Name of the database used by the Secure Heart Information Transmitter. Default is 'doshit'.", default="doshit")
	parser.add_argument("-H", "--databaseHost", type=str, help="The host the database is running on.  Default is 127.0.0.1", default="127.0.0.1")
	parser.add_argument("-U", "--databaseUsername", type=str, help="Username to be used for the database connection. Default is dashit", default="dashit")
	parser.add_argument("-P", "--databasePassword", type=str, help="Password to be used for the database connection. Default is blank", default="Password1!")
	args = parser.parse_args()
	db = SHITDB.SHITdb(args.databaseHost, args.databaseName, args.databaseUsername, args.databasePassword )
	main()