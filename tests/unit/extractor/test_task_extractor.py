from taskflow.backend.extractor.service import TaskExtractor
from taskflow.shared.events import MessageReceived

def test_extract_tasks():
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

test_extract_tasks()