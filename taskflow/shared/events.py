"""
Event schemas for the taskflow application.
All events exchanged between services via RabbitMQ follow these schemas.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import json
from pydantic import BaseModel, Field


class MessageReceived(BaseModel):
    """Event published when a conversation message is received and processed by the ingestor."""

    event_type: str = Field(default="conversation.message_received")
    message_id: str = Field(default="")
    source: str = Field(default="")  # e.g., "slack", "teams", "manual"
    content: str = Field(default="")
    author: str = Field(default="")
    timestamp: Optional[datetime] = None
    channel: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageReceived":
        return cls(**data)


class TaskExtracted(BaseModel):
    """Event published when a task is extracted from a conversation message."""

    event_type: str = Field(default="task.extracted")
    task_id: str = Field(default="")
    source_message_id: str = Field(default="")
    title: str = Field(default="")
    description: str = Field(default="")
    priority: Optional[str] = None  # "low", "medium", "high"
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    labels: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskExtracted":
        return cls(**data)

class TaskCreated(BaseModel):
    """Event published when a task is successfully created in a platform."""

    event_type: str = Field(default="task.created")
    task_id: str = Field(default="")
    platform: str = Field(default="")  # e.g., "trello", "clickup", "console"
    platform_task_id: str = Field(default="")
    title: str = Field(default="")
    created_at: Optional[datetime] = None
    platform_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskCreated":
        return cls(**data)


class TaskFailed(BaseModel):
    """Event published when task creation fails."""

    event_type: str = Field(default="task.failed")
    task_id: str = Field(default="")
    platform: str = Field(default="")
    title: str = Field(default="")
    error_message: str = Field(default="")
    error_code: Optional[str] = None
    failed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskFailed":
        return cls(**data)


def serialize_event(event) -> str:
    """Serialize any event to JSON string."""
    return event.model_dump_json()


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
