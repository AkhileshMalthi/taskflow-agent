from .base_task import BaseTask

class FormattingTask(BaseTask):
    """Task for formatting extracted task details into JSON structure."""
    
    def __init__(self, agent, depends_on=None):
        description = """
        Take the extracted task details and format them into a consistent JSON structure.
        Each task should follow this format:
        {{
          "title": "Task description",
          "assignee": "Person responsible or null if unspecified",
          "dueDate": "ISO format date or null if unspecified"
        }}
        
        Format dates in ISO format (YYYY-MM-DDThh:mm:ss.sssZ) when possible.
        Return a valid JSON array containing all formatted tasks.
        """
        
        expected_output = "A JSON array of properly formatted task objects ready for import."
        
        super().__init__(
            description=description,
            expected_output=expected_output,
            agent=agent,
            depends_on=depends_on
        )
