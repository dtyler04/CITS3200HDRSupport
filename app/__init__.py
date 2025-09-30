from flask import Flask
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from .config import Config 
import os

# Since Templates and static arent part of app, this code says to look in Base_dir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect() 
migrate = Migrate()

def create_app():
    app = Flask(__name__, 
            template_folder=os.path.join(PROJECT_ROOT, 'templates'),
            static_folder=os.path.join(PROJECT_ROOT, 'static')
        )
    
    app.config.from_object(Config)
    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app,db)

    with app.app_context(): 
        from . import models
        db.create_all()
        
        # Initialize default permissions if they don't exist
        init_default_permissions()

    from .routes_admin import admin_bp
    from .routes_OTP import otp_bp
    from .routes import main_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(otp_bp)
    app.register_blueprint(main_bp)

    from .services.emailOTP import EmailOTPService
    from .services.mailchimp_service import MailchimpService
    app.extensions['email_otp']=EmailOTPService(mail)
    app.extensions['mailchimp']=MailchimpService()

    from . import routes

    return app

def init_default_permissions():
    """Initialize default permission types in the Admin table"""
    from .models import Admin
    
    # Check if permissions already exist
    if Admin.query.first() is None:
        # Create default permission types
        student_permission = Admin(permission_number=0, permissionName='student')
        admin_permission = Admin(permission_number=1, permissionName='admin')
        
        db.session.add(student_permission)
        db.session.add(admin_permission)
        db.session.commit()
        
        print("✅ Default permissions initialized:")
        print("   - Permission 0: student")
        print("   - Permission 1: admin")


