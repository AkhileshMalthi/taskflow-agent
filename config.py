import os
from datetime import timedelta

class Config:
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    TESTING = os.getenv('TESTING', 'False').lower() in ('true', '1', 't')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Slack API settings
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
    
    # LLM API settings
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # External integrations
    TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
    TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
    CLICKUP_API_KEY = os.getenv('CLICKUP_API_KEY')
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Task settings
    TASK_REMINDER_WINDOW = int(os.getenv('TASK_REMINDER_WINDOW', '24'))  # hours
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Redis (for job queue)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

config = Config()
