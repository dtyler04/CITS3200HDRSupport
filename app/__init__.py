from flask import Flask

app = Flask(__name__)

# You can configure app settings here, e.g. secret key
app.config['SECRET_KEY'] = 'your_secret_key_here'

from app import routes
