from app import create_app 
flask_app = create_app() 
celery_app = flask_app.extensions['celery']
try:
    from kombu import Connection
    conn = Connection(celery_app.conf.broker_url)
    conn.connect()
    print("✅ Redis broker connected successfully.")
    conn.close()
except Exception as e:
    print(f"⚠️ Redis connection issue: {e}")

if __name__ == '__main__':
    print("✅ Flask app created successfully.")
    print("Celery config (broker):", celery_app.conf.broker_url)
    
    # Force finalization and list tasks (handles config loading)
    try:
        tasks_list = sorted(celery_app.tasks.keys())
        print("Registered Celery tasks:", tasks_list)  # Should include app.tasks.*
        if 'app.tasks.test_task' in tasks_list:
            print("✅ test_task registered OK.")
        else:
            print("⚠️ test_task not found—check imports in app/tasks.py")
    except Exception as e:
        print(f"❌ Error listing tasks: {e}")
        print("   Ensure config.py uses new-style keys (no CELERY_ prefix).")
    
    print("Beat schedule:", celery_app.conf.beat_schedule)