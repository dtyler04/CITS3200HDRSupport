import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
default_database_location = 'sqlite:///' + os.path.join(basedir, 'app.db')
load_dotenv(os.path.join(basedir, ".env"))

class Config:
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or default_database_location
    # You can configure app settings here, e.g. secret key
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_COOKIE_HTTPONLY = True  # JS cannot read cookie
    SESSION_COOKIE_SAMESITE = "Lax" # CSRF protection default
    SESSION_COOKIE_SECURE = False   # Change to True when deploy
    PERMANENT_SESSION_LIFETIME = 1800 # 30 mins lifetime
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")             # your OTP gmail
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")             # 16-char Gmail App Password
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER") or MAIL_USERNAME

    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "false").lower() == "true"
    TESTING = os.getenv("TESTING", "false").lower() == "true"