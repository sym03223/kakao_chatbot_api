from app import app
from app.util.scheduler import scheduler

if __name__ == "__main__":
    scheduler.start()
    app.run(debug=True, host='0.0.0.0', port=5000)