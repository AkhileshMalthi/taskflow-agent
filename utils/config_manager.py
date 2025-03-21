import os
import json
from dotenv import load_dotenv, set_key, find_dotenv
from typing import Dict, Any, Optional

class ConfigManager:
    """Utility for managing configuration settings."""
    
    def __init__(self, env_file: str = None):
        """Initialize the config manager."""
        self.env_file = env_file or find_dotenv()
        if not self.env_file:
            # If no .env file found, use default location
            self.env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        
        # Ensure .env file exists
        if not os.path.exists(self.env_file):
            # Create empty .env file
            with open(self.env_file, 'w') as f:
                f.write("# TaskFlow Agent Configuration\n")
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration values to .env file.
        
        Args:
            config: Dictionary of configuration key-value pairs
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Filter out empty values to avoid overwriting with blanks
            filtered_config = {k: v for k, v in config.items() if v}
            
            for key, value in filtered_config.items():
                set_key(self.env_file, key, value)
            
            # Reload environment variables
            load_dotenv(self.env_file, override=True)
            return True
        except Exception as e:
            print(f"Error saving configuration: {str(e)}")
            return False
    
    def load_config(self) -> Dict[str, str]:
        """
        Load configuration from .env file.
        
        Returns:
            Dict of configuration values
        """
        load_dotenv(self.env_file)
        
        # Return all relevant environment variables
        config = {
            "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "Groq"),
            "LLM_MODEL": os.getenv("LLM_MODEL", "mixtral-8x7b-32768"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
            "TRELLO_API_KEY": os.getenv("TRELLO_API_KEY", ""),
            "TRELLO_API_TOKEN": os.getenv("TRELLO_API_TOKEN", ""),
            "TRELLO_BOARD_ID": os.getenv("TRELLO_BOARD_ID", ""),
            "TRELLO_LIST_ID": os.getenv("TRELLO_LIST_ID", ""),
            "CLICKUP_API_TOKEN": os.getenv("CLICKUP_API_TOKEN", ""),
            "CLICKUP_LIST_ID": os.getenv("CLICKUP_LIST_ID", ""),
            "CLICKUP_SPACE_ID": os.getenv("CLICKUP_SPACE_ID", "")
        }
        
        # Add other LLM provider keys if they exist
        for key in os.environ:
            if key.endswith("_API_KEY") and key not in config:
                config[key] = os.getenv(key, "")
                
        return config
    
    def get_config_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a specific configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        load_dotenv(self.env_file)
        return os.getenv(key, default)
