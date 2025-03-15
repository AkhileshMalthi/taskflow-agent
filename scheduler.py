from datetime import datetime, timedelta
from app import scheduler, db
from models import Task
from slack_bot import slack_bot
import logging

logger = logging.getLogger(__name__)

def check_upcoming_tasks():
    with scheduler.app.app_context():
        try:
            # Find tasks due in the next hour
            now = datetime.utcnow()
            soon = now + timedelta(hours=1)
            
            upcoming_tasks = Task.query.filter(
                Task.due_date.between(now, soon),
                Task.status == 'pending'
            ).all()
            
            for task in upcoming_tasks:
                slack_bot.send_reminder(task)
                
        except Exception as e:
            logger.error(f"Error checking upcoming tasks: {e}")

def init_scheduler():
    # Check for upcoming tasks every 15 minutes
    scheduler.add_job(
        func=check_upcoming_tasks,
        trigger='interval',
        minutes=15,
        id='check_upcoming_tasks',
        replace_existing=True
    )
