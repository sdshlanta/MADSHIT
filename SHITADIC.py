from flask import Flask, render_template, session, request
import SHITDB
import argparse

app = Flask("Alternitive Data Interface Connector")

@app.route('/',methods=['GET', 'POST'])
def index():
	error = None
	if request.method == 'POST':
		if db.checkLogin(request.form['username'], request.form['password']):
			session['username']
		else:
			error = 'Incorrect username or password.'
	else:
		if 'username' in session:
			username = session['username']
		else:
			username = None
		return render_template('index.html', name=username, error=error)
	

def main():

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