import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration for TaskFlow Agent."""
    
    # LLM configuration
    llm_model: str = "groq/mixtral-8x7b-32768"
    llm_api_key: Optional[str] = None
    
    # Task processing configuration
    process_type: str = "sequential"
    verbose: bool = True
    
    # Integration configurations
    slack_api_token: Optional[str] = None
    trello_api_key: Optional[str] = None
    trello_api_token: Optional[str] = None
    clickup_api_token: Optional[str] = None
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        return cls(
            llm_api_key=os.getenv("GROQ_API_KEY"),
            slack_api_token=os.getenv("SLACK_API_TOKEN"),
            trello_api_key=os.getenv("TRELLO_API_KEY"),
            trello_api_token=os.getenv("TRELLO_API_TOKEN"),
            clickup_api_token=os.getenv("CLICKUP_API_TOKEN"),
        )
