from crewai import Agent

class TaskExtractionAgent(Agent):
    """Agent for extracting structured task information from filtered messages."""
    
    def __init__(self, llm):
        super().__init__(
            role="Task Extractor",
            goal="Extract specific task details from messages.",
            backstory="You analyze task-related messages and extract structured information about what needs to be done, by whom, and by when.",
            llm=llm
        )
        
    @classmethod
    def create_default(cls, llm):
        """Create a default instance of the TaskExtractionAgent."""
        return cls(llm)