from flask import Flask, render_template, session, request, redirect, url_for
import SHITDB
import argparse

app = Flask("Alternitive Data Interface Connector")

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
	elif not db.checkForExistingUser(request.form['username']):
		return constructError('Username already taken.', 'renderAddUser')
	try:
		db.insertUser(reqeust.form['username'], request.form['password'], request.form['isAdmin'] == 'admin')
		return constructSuccess('User %s created!'% request.form['username'], 'renderAddUser' )
	except Exception as e:
		return constructError(str(e), 'renderAddUser')

@app.route('/addUser', methods = ['GET'])
def renderAddUser():
	if 'logged_in' not in session:
		return redirect(url_for('index'))
	else:
		return render_template('addUser.html')

def main():
	app.secret_key = "This is some mad SHIT!?!"
	app.run("0.0.0.0", 5000, True)
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser("Secure Heart Information Transmitter Alternitive Data Connector")
	parser.add_argument("-N", "--databaseName", type=str, help="Name of the database used by the Secure Heart Information Transmitter. Default is 'doshit'.", default="doshit")
	parser.add_argument("-H", "--databaseHost", type=str, help="The host the database is running on.  Default is 127.0.0.1", default="127.0.0.1")
	parser.add_argument("-U", "--databaseUsername", type=str, help="Username to be used for the database connection. Default is root", default="daSHIT")
	parser.add_argument("-P", "--databasePassword", type=str, help="Password to be used for the database connection. Default is blank", default="")
	args = parser.parse_args()
	db = SHITDB.SHITdb(args.databaseHost, args.databaseName, args.databaseUsername, args.databasePassword )
	main()