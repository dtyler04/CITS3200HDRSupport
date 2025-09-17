from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, 'app', '.env'))  # ensure env vars are loaded before app import

from app import app, db

# make sure folder for sqlite exists and create tables in context
db_path = os.path.join(BASE_DIR, 'app', 'mydb.sqlite3')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # debug=True for development only
    app.run(host="127.0.0.1", port=5000, debug=True)