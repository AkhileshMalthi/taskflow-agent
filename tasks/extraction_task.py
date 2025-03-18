from .base_task import BaseTask

class ExtractionTask(BaseTask):
    """Task for extracting structured task information from filtered messages."""
    
    def __init__(self, agent, depends_on=None):
        description = """
        Analyze these filtered task-related messages and extract structured task information.
        
        For each message, identify the following components:
        1. Task title: A clear, concise description of what needs to be done (5-10 words)
        2. Task description: More detailed explanation if available
        3. Assignee: The person responsible for completing the task
        4. Deadline: When the task should be completed (be precise with dates)
        5. Priority: Infer priority (High, Medium, Low) based on language and urgency
        6. Status: Default to "To Do" unless otherwise indicated
        
        Follow these extraction rules:
        - If a message mentions someone with "@", they are likely the assignee
        - Words like "urgent", "ASAP", "critical" indicate high priority
        - Time references like "tomorrow", "next week", "by Friday" determine deadline
        - If a deadline is relative (e.g., "tomorrow"), convert it to an actual date
        - If information is missing, use null rather than making assumptions
        
        Return each task as a dictionary with the appropriate fields.
        """
        
        expected_output = "A list of structured task objects with title, description, assignee, deadline, priority, and status fields."
        
        super().__init__(
            description=description,
            expected_output=expected_output,
            agent=agent,
            depends_on=depends_on
        )
