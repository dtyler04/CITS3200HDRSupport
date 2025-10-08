from dotenv import load_dotenv
import os

# 1. Define BASE_DIR (needed to load .env)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Load environment variables
load_dotenv(os.path.join(BASE_DIR, 'app', '.env'))

# 3. Import the create_app function and the db object
from app import create_app, db

# 4. Create the application instance by calling the factory function
app = create_app()

# make sure folder for sqlite exists
db_path = os.path.join(BASE_DIR, 'app', 'mydb.sqlite3')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# The db.create_all() call is also in app/__init__.py, 
# but keeping this ensures your db file is created before run.
# It can be safely removed from here if it works correctly in app/__init__.py
with app.app_context():
    # This call is redundant if it's correctly placed inside create_app
    # but serves as a failsafe here.
    db.create_all()

if __name__ == "__main__":
    # debug=True for development only
    app.run(host="127.0.0.1", port=5000, debug=True)