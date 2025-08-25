# models.py
# Define your database models here


from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = 'users'

	user_id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(50), nullable=False)
	last_name = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(120), nullable=False, unique=True)

	def __repr__(self):
		return f'<User {self.user_id}: {self.first_name} {self.last_name}>'

class Enrollment(db.Model):
		degree_code = db.Column(db.Integer, primary_key=True)
		degree_type = db.Column(db.String(30), nullable=False, unique=True)
	

