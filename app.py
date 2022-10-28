# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import xml.etree.cElementTree as e

app = Flask(__name__)


app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'users'

mysql = MySQL(app)

@app.route('/')
def start():	
	return render_template('registration_copy.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
	print("login in corso")
	msg = 'errore durante il login'
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		print(username)
		password = request.form['password']
		print(password)
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		myquery='SELECT * FROM users WHERE username = "'+str(username)+ '" AND password = "'+str(password)+'"'
		print(myquery)
		cursor.execute(myquery)
		account = cursor.fetchone()
		print(account)
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			myquery='SELECT * FROM journey WHERE user_id ='+str(session['id'])
			cursor.execute(myquery)
			journeys = cursor.fetchall()
			myquery='SELECT * FROM vouchers WHERE user_id ='+str(session['id'])
			cursor.execute(myquery)
			vouchers = cursor.fetchall()
			myquery='SELECT j.name,s.acquired_date,s.used_date FROM `sales` as s join journey as j on j.id=journey_id WHERE s.user_id ='+str(session['id'])
			cursor.execute(myquery)
			sales = cursor.fetchall()
			print(sales)
			return render_template('index.html',sales=sales,vouchers=vouchers, journeys=journeys)
		else:
			msg = 'Incorrect username / password !'
	return render_template('registration_copy.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	print("registering")
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		print("user")
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
		account = cursor.fetchone()
		print(account)
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO accounts VALUES (NULL, "'+str(username)+ '","'+str(password)+'","'+str(email)+'")')
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('registration_copy.html', msg1 = msg)


def scheduled_func():
	print("ciao schedulato")




scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_func, trigger="interval", seconds=60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


	
