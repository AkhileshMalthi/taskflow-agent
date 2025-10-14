"""
Unit tests for TaskExtractor service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from taskflow.backend.extractor.service import TaskExtractor
from taskflow.shared.events import MessageReceived, TaskExtracted
from taskflow.models.extractor import LLMResponse, RawTask


@pytest.fixture
def mock_llm():
    """Fixture to mock the LLM."""
    with patch('taskflow.backend.extractor.service.get_llm') as mock:
        llm_instance = MagicMock()
        structured_llm = MagicMock()
        
        # Create a mock response with tasks using RawTask
        mock_response = LLMResponse(
            tasks=[
                RawTask(
                    title="Fix the login bug",
                    description="Fix the login bug by Friday",
                    priority="high",
                    due_date=datetime(2025, 10, 18, tzinfo=timezone.utc),
                    assigned_to="john",
                    labels=["bug", "urgent"]
                )
            ]
        )
        
        structured_llm.invoke.return_value = mock_response
        llm_instance.with_structured_output.return_value = structured_llm
        mock.return_value = llm_instance
        
        yield mock


def test_extract_tasks_basic(mock_llm):
    """Test basic task extraction from a message."""
    extractor = TaskExtractor()
    message = MessageReceived(
        message_id="msg-001",
        source="slack",
        content="We need to fix the login bug by Friday. @john please update the documentation ASAP.",
        author="alice",
        timestamp=None,
        channel="general"
    )
    
    tasks = extractor.extract_tasks(message)
    
    # Verify we got tasks back
    assert tasks is not None
    assert isinstance(tasks, list)
    assert len(tasks) > 0
    
    # Verify task properties
    first_task = tasks[0]
    assert isinstance(first_task, TaskExtracted)
    assert first_task.title == "Fix the login bug"
    assert first_task.source_message_id == "msg-001"
    assert first_task.priority == "high"


def test_extract_tasks_empty_message(mock_llm):
    """Test that empty messages are handled gracefully."""
    # Modify mock to return no tasks
    mock_llm.return_value.with_structured_output.return_value.invoke.return_value = LLMResponse(tasks=[])
    
    extractor = TaskExtractor()
    message = MessageReceived(
        message_id="msg-002",
        source="slack",
        content="",
        author="bob",
        timestamp=None,
        channel="general"
    )
    
    tasks = extractor.extract_tasks(message)
    
    assert tasks is not None
    assert isinstance(tasks, list)
    assert len(tasks) == 0


def test_extract_tasks_multiple_tasks(mock_llm):
    """Test extraction of multiple tasks from a single message."""
    # Mock response with multiple tasks
    mock_response = LLMResponse(
        tasks=[
            RawTask(
                title="Fix login bug",
                description="Fix the login issue",
                priority="high",
                due_date=datetime(2025, 10, 18, tzinfo=timezone.utc)
            ),
            RawTask(
                title="Update documentation",
                description="Update the API docs",
                priority="medium",
                assigned_to="john"
            )
        ]
    )
    
    mock_llm.return_value.with_structured_output.return_value.invoke.return_value = mock_response
    
    extractor = TaskExtractor()
    message = MessageReceived(
        message_id="msg-003",
        source="slack",
        content="We need to fix the login bug by Friday. @john please update the documentation ASAP.",
        author="alice",
        timestamp=None,
        channel="general"
    )
    
    tasks = extractor.extract_tasks(message)
    
    assert len(tasks) == 2
    assert tasks[0].title == "Fix login bug"
    assert tasks[1].title == "Update documentation"


