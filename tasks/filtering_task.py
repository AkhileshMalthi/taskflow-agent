from .base_task import BaseTask
from datetime import datetime

class FilteringTask(BaseTask):
    """Task for filtering out task-related messages from conversations."""
    
    def __init__(self, agent):
        # First create the template with the current date
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        description = f"""
        Review the provided Slack messages and identify only those that contain task-related information.
        
        Today's date is: {today_date}
        
        Task-related messages typically include:
        - Work assignments (e.g., "Can you fix this?", "Please implement this")
        - Deadlines (e.g., "by tomorrow", "next week")
        - Commitments to do something (e.g., "I'll work on this")
        - Follow-ups or status updates on existing work
        - Messages containing action verbs followed by project components
        
        DO NOT include messages that are:
        - Purely social or greeting messages
        - Questions without assignment of work
        - General statements without actionable items
        - Acknowledgments without commitment (e.g., "Sounds good")
        
        For context, these messages are being used to extract tasks for a project management system.
        
        Here are the messages to filter:
        {{messages}}
        
        For each message you keep, explain:
        1. What task-related information it contains
        2. Who might be responsible for the task
        3. If there's any deadline or priority information
        
        Return only the messages that contain task information with your analysis for each.
        """
        
        expected_output = "A list of filtered messages containing only task-related information with analyses."
        
        super().__init__(
            description=description,
            expected_output=expected_output,
            agent=agent
        )
