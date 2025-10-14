"""
CRUD operations for tasks and messages using SQLAlchemy ORM.
"""
from sqlalchemy.orm import Session
from .models import Message, Task
from datetime import datetime, timezone
from typing import Optional
def create_message(db: Session, source: str, content: str, author: str, channel: Optional[str] = None, metadata: Optional[dict] = None) -> Message:
    msg = Message(
        source=source,
        content=content,
        author=author,
        channel=channel,
        metadata=metadata or {},
        timestamp=datetime.now(timezone.utc)
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_message(db: Session, message_id):
    return db.query(Message).filter(Message.id == message_id).first()

def create_task(db: Session, source_message_id, title, description=None, priority=None, due_date=None, assigned_to=None, labels=None, platform=None, platform_task_id=None, status=None) -> Task:
    task = Task(
        source_message_id=source_message_id,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        assigned_to=assigned_to,
        labels=labels or [],
        platform=platform,
        platform_task_id=platform_task_id,
        status=status,
        created_at=datetime.now(timezone.utc)
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_task(db: Session, task_id):
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks_by_message(db: Session, message_id):
    return db.query(Task).filter(Task.source_message_id == message_id).all()
