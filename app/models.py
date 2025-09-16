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

    updates = db.relationship('EnrollmentUpdate', backref='user', lazy=True)

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
class Permission(db.Model):
    __tablename__ = 'Permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g. 'edit_email', 'manage_users'

class UserPermission(db.Model):
    __tablename__ = 'UserPermissions'
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('Permissions.id'), primary_key=True)

    user = db.relationship('User', backref=db.backref('user_permissions', lazy='dynamic'))
    permission = db.relationship('Permission', backref=db.backref('user_permissions', lazy='dynamic'))

def create_default_permissions():
    defaults = ["default", "view_admin_dashboard", "edit_email", "view_users", "manage_users", "student_stats"]
    for name in defaults:
        if not Permission.query.filter_by(name=name).first():
            db.session.add(Permission(name=name))
    db.session.commit()