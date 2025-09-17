# models.py
# Define your database models here


from app import db

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
    degreeCode = db.Column(db.String(8), db.ForeignKey('Enrollments.degreeCode'), nullable=False)
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
    degreeCode = db.Column(db.String(8), db.ForeignKey('Enrollments.degreeCode'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    week_released = db.Column(db.Integer, nullable=False)
class Assessments(db.Model):
    __tablename__ = 'Assessments'
    assessment_id = db.Column(db.Integer, primary_key=True)
    degreeCode = db.Column(db.String(8), db.ForeignKey('Enrollments.degreeCode'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_week = db.Column(db.Integer, nullable=False)

    enrollment = db.relationship('Enrollment', backref='assessments', lazy=True)
class EmailLog(db.Model):
    __tablename__ = 'EmailLogs'
    email_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=False)
    mailchimp_id = db.Column(db.String(255), nullable=True)  # To store Mailchimp message ID for reference
    
    user = db.relationship('User', backref='email_logs', lazy=True)

    