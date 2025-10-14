"""
SQLAlchemy models for persistent storage of tasks and messages.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime, timezone

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    channel = Column(String, nullable=True)
    metadata = Column(JSONB, nullable=True)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    assigned_to = Column(String, nullable=True)
    labels = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    platform = Column(String, nullable=True)
    platform_task_id = Column(String, nullable=True)
    status = Column(String, nullable=True)
