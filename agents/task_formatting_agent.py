from crewai import Agent

class TaskFormattingAgent(Agent):
    """Agent for formatting extracted task details into JSON format."""
    
    def __init__(self, llm):
        super().__init__(
            role="Task Formatter",
            goal="Format extracted tasks into a standard JSON format.",
            backstory="You transform raw task data into properly formatted JSON that can be imported into task management systems.",
            llm=llm
        )
        
    @classmethod
    def create_default(cls, llm):
        """Create a default instance of the TaskFormattingAgent."""
        return cls(llm)