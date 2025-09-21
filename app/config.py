import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
default_database_location = 'sqlite:///' + os.path.join(basedir, 'app.db')

class Config:
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or default_database_location
    # You can configure app settings here, e.g. secret key
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_COOKIE_HTTPONLY = True  # JS cannot read cookie
    SESSION_COOKIE_SAMESITE = "Lax" # CSRF protection default
    SESSION_COOKIE_SECURE = False   # Change to True when deploy
    PERMANENT_SESSION_LIFETIME = 1800 # 30 mins lifetime

    # file uploads for support posts
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4 MB