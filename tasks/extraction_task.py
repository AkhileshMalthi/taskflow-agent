from .base_task import BaseTask

class ExtractionTask(BaseTask):
    """Task for extracting structured task information from filtered messages."""
    
    def __init__(self, agent, depends_on=None):
        description = """
        Analyze these filtered task-related messages and extract structured task information.
        For each message, identify:
        1. Task title/description (what needs to be done)
        2. Assignee (who is responsible)
        3. Deadline (when it's due)
        
        Return a list of structured tasks, each with title, assignee, and deadline fields.
        """
        
        expected_output = "A list of structured task objects with title, assignee, and deadline fields."
        
        super().__init__(
            description=description,
            expected_output=expected_output,
            agent=agent,
            depends_on=depends_on
        )
