import os
import logging
from flask import Flask
from extensions import db, scheduler
from config import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    
    # Configure Flask app
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    
    # Use DATABASE_URL from environment, provided by create_postgresql_database_tool
    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///tasks.db"
    
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)
    # Don't start scheduler here - we'll do it in the main block
    
    with app.app_context():
        # Import models before creating tables
        from models import Session, Conversation, Task
    
    # Register blueprints
    from routes import main_bp, api_bp, slack_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(slack_bp, url_prefix='/slack')
    
    return app

# Create application instance
app = create_app()

def init_db():
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")

if __name__ == '__main__':
    # Only start scheduler once when running the app directly
    if not scheduler.running:
        scheduler.start()
    init_db()
    app.run(debug=True)