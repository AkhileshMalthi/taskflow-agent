from crewai import Task

class BaseTask(Task):
    """Base class for all tasks in the TaskFlow system."""
    
    def __init__(self, description, expected_output, agent, depends_on=None):
        super().__init__(
            description=description,
            expected_output=expected_output,
            agent=agent,
            depends_on=depends_on or []
        )
