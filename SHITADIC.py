from flask import Flask, render_template, session, request, redirect, url_for
import SHITDB
import argparse

app = Flask("Alternitive Data Interface Connector")

@app.route('/',methods=['GET', 'POST'])
def index():
	error = None
	if request.method == 'POST':
		if db.checkUserCreds(request.form['username'], request.form['password']):
			session['username'] = request.form['username']
			session['logged_in'] = True
			username = session['username']
		else:
			error = 'Incorrect username or password.'
			
	else:
		if 'username' in session:
			session['logged_in'] = True
			username = session['username']
		else:
			username = None
	return render_template('index.html', name=username, error=error)

@app.route('/logout', methods=['GET'])
def logout():
	if 'logged_in' in session:
		del session['logged_in']
	if 'username' in session:
		del session['username']
	return redirect(url_for('index'))

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