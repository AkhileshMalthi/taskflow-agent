from crewai import Agent

class FilteringAgent(Agent):
    """Agent for filtering task-related messages from a conversation."""
    
    def __init__(self, llm):
        super().__init__(
            role="Task Filter",
            goal="Identify messages that contain task-related information.",
            backstory="You are an AI that filters Slack messages, keeping only those related to task assignments, deadlines, or work requests.",
            llm=llm
        )
        
    @classmethod
    def create_default(cls, llm):
        """Create a default instance of the FilteringAgent."""
        return cls(llm)