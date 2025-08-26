
from app import app
from flask import render_template

# Both of these direct to the welcome page
@app.route('/')
def index():
	return render_template('welcome.html')

@app.route('/welcome')
def welcome():
	return render_template('welcome.html')

# Login page route
@app.route('/login')
def login():
	return render_template('login.html')

# Admin dashboard route
@app.route('/admin')
def admin_dashboard():
	return render_template('admin_dashboard.html')

# Student dashboard route
@app.route('/student')
def student_dashboard():
	return render_template('student_dashboard.html')
