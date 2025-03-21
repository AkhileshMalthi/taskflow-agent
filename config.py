import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class Config:
    """Configuration for TaskFlow Agent."""
    
    # LLM configuration
    llm_provider: str = "Groq"  # Default LLM provider
    llm_model: str = "mixtral-8x7b-32768"  # Default model
    llm_credentials: Dict[str, str] = field(default_factory=dict)
    
    # Task processing configuration
    process_type: str = "sequential"
    verbose: bool = True
    
    # Integration configurations
    slack_api_token: Optional[str] = None
    
    # Trello configurations
    trello_api_key: Optional[str] = None
    trello_api_token: Optional[str] = None
    trello_board_id: Optional[str] = None
    trello_list_id: Optional[str] = None
    
    # ClickUp configurations
    clickup_api_token: Optional[str] = None
    clickup_list_id: Optional[str] = None
    clickup_space_id: Optional[str] = None
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        config = cls(
            llm_provider=os.getenv("LLM_PROVIDER", "Groq"),
            llm_model=os.getenv("LLM_MODEL", "mixtral-8x7b-32768"),
            slack_api_token=os.getenv("SLACK_API_TOKEN"),
            
            trello_api_key=os.getenv("TRELLO_API_KEY"),
            trello_api_token=os.getenv("TRELLO_API_TOKEN"),
            trello_board_id=os.getenv("TRELLO_BOARD_ID"),
            trello_list_id=os.getenv("TRELLO_LIST_ID"),
            
            clickup_api_token=os.getenv("CLICKUP_API_TOKEN"),
            clickup_list_id=os.getenv("CLICKUP_LIST_ID"),
            clickup_space_id=os.getenv("CLICKUP_SPACE_ID"),
        )
        
        # Load LLM credentials from environment variables
        config.llm_credentials = {
            "api_key": os.getenv("GROQ_API_KEY"),
        }
        
        return config
