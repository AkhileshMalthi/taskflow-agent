from datetime import datetime
from extensions import db

# Database Models
class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.String(50), nullable=False)
    started_by = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, ended
    
    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'started_by': self.started_by,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status
        }

class Conversation(db.Model):
    __tablename__ = 'conversation'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    context_type = db.Column(db.String(20), nullable=True)  # task_mention, assignment, general
    context = db.Column(db.Text, nullable=True)  # Additional context for better task extraction
    thread_ts = db.Column(db.String(50), nullable=True)
    reply_count = db.Column(db.Integer, default=0)
    
    # Define relationship after both models are defined
    session = db.relationship('Session', backref=db.backref('conversations', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'context_type': self.context_type,
            'context': self.context,
            'thread_ts': self.thread_ts,
            'reply_count': self.reply_count
        }

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    assigned_to = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, blocked
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    slack_thread_ts = db.Column(db.String(50), nullable=True)
    external_id = db.Column(db.String(100), nullable=True)  # Trello/Clickup task ID
    external_service = db.Column(db.String(20), nullable=True)  # 'trello' or 'clickup'
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=True)
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_by = db.Column(db.String(50), nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Define relationship after both models are defined
    session = db.relationship('Session', backref=db.backref('tasks', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'priority': self.priority,
            'slack_thread_ts': self.slack_thread_ts,
            'external_id': self.external_id,
            'external_service': self.external_service,
            'approval_status': self.approval_status,
            'created_by': self.created_by,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }