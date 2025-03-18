from .base_task import BaseTask

class FilteringTask(BaseTask):
    """Task for filtering out task-related messages from conversations."""
    
    def __init__(self, agent):
        description = """
        Review the provided Slack messages and identify only those that contain task-related information.
        Task-related messages typically include:
        - Work assignments (e.g., "Can you fix this?", "Please implement this")
        - Deadlines (e.g., "by tomorrow", "next week")
        - Commitments to do something (e.g., "I'll work on this")
        
        Here are the messages to filter:
        {messages}
        
        Return only the messages that contain task information and explain why you kept each one.
        """
        
        expected_output = "A list of filtered messages containing only task-related information with explanations."
        
        super().__init__(
            description=description,
            expected_output=expected_output,
            agent=agent
        )
