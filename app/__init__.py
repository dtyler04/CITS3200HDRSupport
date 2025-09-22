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

    from .routes_admin import admin_bp
    from .routes_OTP import otp_bp
    from .routes import main_bp
    from .routes_unit import unit_bp 
    app.register_blueprint(admin_bp)
    app.register_blueprint(otp_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(unit_bp)

    from .services.emailOTP import EmailOTPService
    from .services.mailchimp_service import MailchimpService
    app.extensions['email_otp']=EmailOTPService(mail)
    app.extensions['mailchimp']=MailchimpService()

    return app
