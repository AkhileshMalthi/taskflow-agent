from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid

class RawTask(BaseModel):
    """Represents a task extracted from a message, without a unique identifier.
    
    Attributes:
        title (str): The title of the task.
        description (str): A detailed description of the task.
        priority (Optional[str]): The priority level of the task ("low", "medium", "high").
        due_date (Optional[datetime]): The due date for the task, if any.
        assigned_to (Optional[str]): The person assigned to the task, if any.
        labels (Optional[List[str]]): A list of labels or tags associated with the task.
    """
    title: str = Field(default="")
    description: str = Field(default="")
    priority: Optional[str] = None  # "low", "medium", "high"
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    labels: Optional[List[str]] = Field(default_factory=list)

class LLMResponse(BaseModel):
    """
    Represents the response from a language model containing extracted tasks.

    Attributes:
        tasks (List[RawTask]): A list of tasks extracted from the language model's response.
    """
    tasks: List[RawTask] = Field(default_factory=list)

class Task(RawTask):
    """Represents a task with a unique identifier.
    
    Attributes:
        task_id (str): The unique identifier for the task.
    """
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))