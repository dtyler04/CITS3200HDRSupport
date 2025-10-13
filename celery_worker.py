from app import create_app

# Create the Flask app (so all extensions load)
flask_app = create_app()

# Grab the Celery instance that was initialized in app/__init__.py
celery_app = flask_app.extensions["celery"]

# Optional: expose for Celery CLI entry point
app = celery_app
