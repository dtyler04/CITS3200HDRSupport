# models.py
# Define your database models here


from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    rights = db.relationship('Right', backref='user', lazy=True)
    updates = db.relationship('EnrollmentUpdate', backref='user', lazy=True)
class Right(db.Model):
    __tablename__ = 'Rights'
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False, primary_key=True)
    permission_number = db.Column(db.Integer, db.ForeignKey('Admin.permission_number'), primary_key=True)
    
class Admin(db.Model):
    __tablename__ = 'Admin'
    permission_number = db.Column(db.Integer, primary_key=True)
    permissionName = db.Column(db.String(50), nullable=False)

    rights = db.relationship('Right', backref='admin', lazy=True)
class EnrollmentUpdate(db.Model):
    __tablename__ = 'EnrollmentUpdates'
    update_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    degreeCode = db.Column(db.String, db.ForeignKey('Enrollments.degreeCode'), nullable=False)
    initialisation = db.Column(db.Boolean, nullable=False)
    study_mode = db.Column(db.String, nullable=False)
    current_week = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String, nullable=False)
class Enrollment(db.Model):
    __tablename__ = 'Enrollments'
    degreeCode = db.Column(db.String(8), primary_key=True)
    degree_type = db.Column(db.String, nullable=False)

    updates = db.relationship('EnrollmentUpdate', backref='enrollment', lazy=True)
    messages = db.relationship('Message', backref='enrollment', lazy=True)
class Message(db.Model):
    __tablename__ = 'Messages'
    message_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)               # new
    degreeCode = db.Column(db.String(8), db.ForeignKey('Enrollments.degreeCode'), nullable=True)
    message_content = db.Column(db.Text, nullable=False)
    week_released = db.Column(db.Integer, nullable=True)
    scheduled_at = db.Column(db.DateTime, nullable=True)            # new: schedule time
    degree_type_target = db.Column(db.String(20), nullable=True)    # 'masters','phd' or NULL for all
    location_target = db.Column(db.String(20), nullable=True)       # 'online','on-campus' or NULL
    stage_target = db.Column(db.String(30), nullable=True)          # 'commencing' etc or NULL

class Reminder(db.Model):
    __tablename__ = 'Reminders'
    reminder_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    degree_type_target = db.Column(db.String(20), nullable=True)
    location_target = db.Column(db.String(20), nullable=True)
    stage_target = db.Column(db.String(30), nullable=True)

class SupportPost(db.Model):
    __tablename__ = 'SupportPosts'
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupportContact(db.Model):
    __tablename__ = 'SupportContacts'
    contact_id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(100), nullable=False)   # e.g. 'Mental Health'
    name = db.Column(db.String(200), nullable=False)
    info = db.Column(db.String(300), nullable=False)

