from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config 
import os

# Since ../templates and ../static/ are not child of ./app  
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

db = SQLAlchemy()
app = Flask(__name__, 
            template_folder=os.path.join(PROJECT_ROOT, 'templates'),
            static_folder=os.path.join(PROJECT_ROOT, 'static')
        )
app.config.from_object(Config)
db.init_app(app)
with app.app_context(): 
    from . import models
    db.create_all()

from . import routes 
