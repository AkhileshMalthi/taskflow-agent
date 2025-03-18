import json
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class TaskExporter(ABC):
    """Base class for exporting tasks to external systems."""
    
    @abstractmethod
    def export_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Export the tasks to the external system."""
        pass

class TrelloExporter(TaskExporter):
    """Export tasks to Trello."""
    
    def __init__(self, api_key: str = None, token: str = None, board_id: str = None):
        self.api_key = api_key or os.getenv("TRELLO_API_KEY")
        self.token = token or os.getenv("TRELLO_API_TOKEN")
        self.board_id = board_id or os.getenv("TRELLO_BOARD_ID")
        
        if not self.api_key or not self.token:
            raise ValueError("Trello API key and token are required. Set TRELLO_API_KEY and TRELLO_API_TOKEN environment variables.")
        
    def export_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Export tasks to Trello."""
        try:
            # Implementation would go here using the Trello API
            print(f"Exporting {len(tasks)} tasks to Trello")
            return True
        except Exception as e:
            print(f"Error exporting to Trello: {str(e)}")
            raise

class ClickUpExporter(TaskExporter):
    """Export tasks to ClickUp."""
    
    def __init__(self, api_token: str = None, list_id: str = None):
        self.api_token = api_token or os.getenv("CLICKUP_API_TOKEN")
        self.list_id = list_id or os.getenv("CLICKUP_LIST_ID")
        
        if not self.api_token:
            raise ValueError("ClickUp API token is required. Set CLICKUP_API_TOKEN environment variable.")
        
    def export_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Export tasks to ClickUp."""
        try:
            # Implementation would go here using the ClickUp API
            print(f"Exporting {len(tasks)} tasks to ClickUp")
            return True
        except Exception as e:
            print(f"Error exporting to ClickUp: {str(e)}")
            raise

class FileExporter(TaskExporter):
    """Export tasks to a JSON file."""
    
    def __init__(self, output_dir: str = "d:\\Projects\\taskflow-agent\\output"):
        self.output_dir = output_dir
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Could not create output directory: {str(e)}")
        
    def export_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Export tasks to a JSON file."""
        filename = os.path.join(self.output_dir, f"tasks_{self._get_timestamp()}.json")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2)
            print(f"Tasks exported to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting tasks: {str(e)}")
            raise
            
    def _get_timestamp(self) -> str:
        """Get a timestamp string for the filename."""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
