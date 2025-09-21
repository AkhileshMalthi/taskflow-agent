"""
Event schemas for the taskflow application.
All events exchanged between services via RabbitMQ follow these schemas.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class MessageReceived:
    """Event published when a conversation message is received and processed by the ingestor."""
    
    event_type: str = "conversation.message_received"
    message_id: str = ""
    source: str = ""  # e.g., "slack", "teams", "manual"
    content: str = ""
    author: str = ""
    timestamp: Optional[datetime] = None
    channel: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_type": self.event_type,
            "message_id": self.message_id,
            "source": self.source,
            "content": self.content,
            "author": self.author,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "channel": self.channel,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageReceived":
        """Create instance from dictionary."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])
        
        return cls(
            event_type=data.get("event_type", "conversation.message_received"),
            message_id=data.get("message_id", ""),
            source=data.get("source", ""),
            content=data.get("content", ""),
            author=data.get("author", ""),
            timestamp=timestamp,
            channel=data.get("channel"),
            metadata=data.get("metadata", {})
        )


@dataclass
class TaskExtracted:
    """Event published when a task is extracted from a conversation message."""
    
    event_type: str = "task.extracted"
    task_id: str = ""
    source_message_id: str = ""
    title: str = ""
    description: str = ""
    priority: Optional[str] = None  # "low", "medium", "high"
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    labels: Optional[list] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_type": self.event_type,
            "task_id": self.task_id,
            "source_message_id": self.source_message_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "assigned_to": self.assigned_to,
            "labels": self.labels or [],
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskExtracted":
        """Create instance from dictionary."""
        due_date = None
        if data.get("due_date"):
            due_date = datetime.fromisoformat(data["due_date"])
        
        return cls(
            event_type=data.get("event_type", "task.extracted"),
            task_id=data.get("task_id", ""),
            source_message_id=data.get("source_message_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            priority=data.get("priority"),
            due_date=due_date,
            assigned_to=data.get("assigned_to"),
            labels=data.get("labels", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class TaskCreated:
    """Event published when a task is successfully created in a platform."""
    
    event_type: str = "task.created"
    task_id: str = ""
    platform: str = ""  # e.g., "trello", "clickup", "console"
    platform_task_id: str = ""
    title: str = ""
    created_at: Optional[datetime] = None
    platform_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_type": self.event_type,
            "task_id": self.task_id,
            "platform": self.platform,
            "platform_task_id": self.platform_task_id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "platform_url": self.platform_url,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskCreated":
        """Create instance from dictionary."""
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        
        return cls(
            event_type=data.get("event_type", "task.created"),
            task_id=data.get("task_id", ""),
            platform=data.get("platform", ""),
            platform_task_id=data.get("platform_task_id", ""),
            title=data.get("title", ""),
            created_at=created_at,
            platform_url=data.get("platform_url"),
            metadata=data.get("metadata", {})
        )


@dataclass
class TaskFailed:
    """Event published when task creation fails."""
    
    event_type: str = "task.failed"
    task_id: str = ""
    platform: str = ""
    title: str = ""
    error_message: str = ""
    error_code: Optional[str] = None
    failed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_type": self.event_type,
            "task_id": self.task_id,
            "platform": self.platform,
            "title": self.title,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "failed_at": self.failed_at.isoformat() if self.failed_at else None,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskFailed":
        """Create instance from dictionary."""
        failed_at = None
        if data.get("failed_at"):
            failed_at = datetime.fromisoformat(data["failed_at"])
        
        return cls(
            event_type=data.get("event_type", "task.failed"),
            task_id=data.get("task_id", ""),
            platform=data.get("platform", ""),
            title=data.get("title", ""),
            error_message=data.get("error_message", ""),
            error_code=data.get("error_code"),
            failed_at=failed_at,
            metadata=data.get("metadata", {})
        )


def serialize_event(event) -> str:
    """Serialize any event to JSON string."""
    return json.dumps(event.to_dict())


def deserialize_event(event_json: str, event_type: str):
    """Deserialize JSON string to appropriate event object."""
    data = json.loads(event_json)
    
    if event_type == "conversation.message_received":
        return MessageReceived.from_dict(data)
    elif event_type == "task.extracted":
        return TaskExtracted.from_dict(data)
    elif event_type == "task.created":
        return TaskCreated.from_dict(data)
    elif event_type == "task.failed":
        return TaskFailed.from_dict(data)
    else:
        raise ValueError(f"Unknown event type: {event_type}")