from flask import Flask
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from .config import Config 
import os
import logging
from logging.handlers import RotatingFileHandler
from celery import Celery, Task
from celery.schedules import crontab

# Since Templates and static arent part of app, this code says to look in Base_dir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect() 
migrate = Migrate()
celery = Celery()

def create_app():
    app = Flask(__name__, 
            template_folder=os.path.join(PROJECT_ROOT, 'templates'),
            static_folder=os.path.join(PROJECT_ROOT, 'static')
        )
    app.config.update(
        broker_url="redis://localhost:6379/0",
        result_backend="redis://localhost:6379/0",
        task_ignore_result=False,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Australia/Perth",
        enable_utc=True,
        beat_schedule={
            "run-daily-job": {
                "task": "app.tasks.daily_progression_check",
                "schedule": crontab(hour=2, minute=0),
            },
        },
    )
    
    app.config.from_prefixed_env()  # Loads env vars (e.g., BROKER_URL=... overrides)
    app.config.from_object(Config)

    app.config.from_object(Config)
    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app,db)
    celery_init_app(app)

    with app.app_context(): 
        from . import models
        from .tasks import daily_progression_check, test_task
        db.create_all()
        
        # Initialize default permissions if they don't exist
        init_default_permissions()

    from .routes_admin import admin_bp
    from .routes_OTP import otp_bp
    from .routes import main_bp
    from .routes_unit import unit_bp 
    from .routes_webhook import mailchimp_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(otp_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(unit_bp)
    app.register_blueprint(mailchimp_bp)

    from .services.emailOTP import EmailOTPService
    from .services.mailchimp_service import MailchimpService
    app.extensions['email_otp']=EmailOTPService(mail)
    app.extensions['mailchimp']=MailchimpService()

    from . import routes

    # Configure logging for production
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(PROJECT_ROOT, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Set up file handler
        file_handler = RotatingFileHandler(
            os.path.join(logs_dir, 'app.log'), 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('HDR Support application startup')

    return app

def init_default_permissions():
    """Initialize default permission types in the Admin table"""
    from .models import Admin
    
    try:
        # Check if permissions already exist
        if Admin.query.first() is None:
            # Create default permission types
            student_permission = Admin(permission_number=0, permission_name='student')
            admin_permission = Admin(permission_number=1, permission_name='admin')
            
            db.session.add(student_permission)
            db.session.add(admin_permission)
            db.session.commit()
            
            print("✅ Default permissions initialized:")
            print("   - Permission 0: student")
            print("   - Permission 1: admin")
    except Exception as e:
        # Handle case where table structure doesn't match model
        print(f"⚠️  Database schema mismatch: {e}")
        print("   Run 'flask db upgrade' to update database schema")
        # Don't fail startup - let the app run and admin can fix schema
        db.session.rollback()

def celery_init_app(app: Flask) -> Celery:
    """Configure Celery with Flask app context."""
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    # Apply config
    celery.Task = FlaskTask
    celery.set_default()
    celery_app.conf.update(app.config)
    app.extensions["celery"] = celery_app
    return celery_app