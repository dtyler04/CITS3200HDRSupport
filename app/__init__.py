from flask import Flask
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from .config import Config 
import os

# Since Templates and static arent part of app, this code says to look in Base_dir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

db = SQLAlchemy()
app = Flask(__name__, 
            template_folder=os.path.join(PROJECT_ROOT, 'templates'),
            static_folder=os.path.join(PROJECT_ROOT, 'static')
        )
app.config.from_object(Config)
csrf = CSRFProtect(app) 
db.init_app(app)
with app.app_context(): 
    from . import models
    db.create_all()

from .routes_admin import admin_bp
app.register_blueprint(admin_bp )
from . import routes
