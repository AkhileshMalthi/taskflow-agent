from .base_task import BaseTask

class FormattingTask(BaseTask):
    """Task for formatting extracted task details into JSON structure."""
    
    def __init__(self, agent, depends_on=None):
        description = """
        Take the extracted task details and format them into a consistent JSON structure.
        
        For each task, include these fields:
        - title: A clear task description
        - description: Detailed explanation or null if unavailable
        - assignee: Person responsible or null if unspecified
        - dueDate: ISO format date or null if unspecified
        - priority: High, Medium, or Low
        - status: To Do, In Progress, or Done
        - createdAt: Current timestamp in ISO format
        - taskId: A unique ID (UUID format preferred)
        
        Formatting requirements:
        - Format dates in ISO 8601 format (YYYY-MM-DDThh:mm:ss.sssZ)
        - Generate a unique taskId for each task
        - Set the createdAt field to the current time
        - For missing fields, use null instead of empty strings
        - Ensure the JSON is properly formatted and valid
        
        Return a valid JSON array containing all formatted tasks.
        """
        
        expected_output = "A JSON array of properly formatted task objects ready for import into task management systems."
        
        super().__init__(
            description=description,
            expected_output=expected_output,
            agent=agent,
            depends_on=depends_on
        )
