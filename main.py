from app import app
from scheduler import init_scheduler

if __name__ == "__main__":
    init_scheduler()
    app.run(host="0.0.0.0", port=5000, debug=True)
