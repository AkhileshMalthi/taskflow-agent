import json
import os
import uuid
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

class TaskExporter(ABC):
    """Base class for exporting tasks to external systems."""
    
    @abstractmethod
    def export_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Export the tasks to the external system."""
        pass

class TrelloExporter(TaskExporter):
    """Export tasks to Trello."""
    
    def __init__(self, api_key: str = None, token: str = None, board_id: str = None, list_id: str = None):
        self.api_key = api_key or os.getenv("TRELLO_API_KEY")
        self.token = token or os.getenv("TRELLO_API_TOKEN")
        self.board_id = board_id or os.getenv("TRELLO_BOARD_ID")
        self.list_id = list_id or os.getenv("TRELLO_LIST_ID")
        self.base_url = "https://api.trello.com/1"
        
        if not self.api_key or not self.token:
            raise ValueError("Trello API key and token are required. Set TRELLO_API_KEY and TRELLO_API_TOKEN environment variables.")
        
        # If no list ID is provided but a board ID is, get the first list on the board
        if not self.list_id and self.board_id:
            self.list_id = self._get_first_list_id()
        
        if not self.list_id:
            raise ValueError("Trello list ID is required. Either set TRELLO_LIST_ID or provide a board ID.")
    
    def _get_first_list_id(self) -> str:
        """Get the ID of the first list on the board."""
        url = f"{self.base_url}/boards/{self.board_id}/lists"
        params = {
            "key": self.api_key,
            "token": self.token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            lists = response.json()
            
            if lists:
                return lists[0]["id"]
            else:
                raise ValueError("No lists found on the specified Trello board")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Trello lists: {str(e)}")
            raise
    
    def _create_card(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Trello card for the task."""
        url = f"{self.base_url}/cards"
        
        # Format due date if available
        due_date = task.get("dueDate")
        
        # Build description with all details
        description = ""
        if task.get("description"):
            description += f"{task['description']}\n\n"
        
        description += f"Priority: {task.get('priority', 'Medium')}\n"
        description += f"Status: {task.get('status', 'To Do')}\n"
        
        if task.get("taskId"):
            description += f"\nTask ID: {task['taskId']}"
        
        # Create the card
        params = {
            "key": self.api_key,
            "token": self.token,
            "idList": self.list_id,
            "name": task["title"],
            "desc": description,
            "pos": "bottom"
        }
        
        # Add due date if available
        if due_date:
            params["due"] = due_date
        
        # Add label based on priority
        if task.get("priority") == "High":
            params["idLabels"] = self._get_label_id("red")
        elif task.get("priority") == "Medium":
            params["idLabels"] = self._get_label_id("yellow")
        elif task.get("priority") == "Low":
            params["idLabels"] = self._get_label_id("green")
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating Trello card: {str(e)}")
            raise
    
    def _get_label_id(self, color: str) -> str:
        """Get or create a label ID for the specified color on the board."""
        url = f"{self.base_url}/boards/{self.board_id}/labels"
        params = {
            "key": self.api_key,
            "token": self.token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            labels = response.json()
            
            # Look for existing label with the specified color
            for label in labels:
                if label["color"] == color:
                    return label["id"]
            
            # If no label exists with that color, create one
            return self._create_label(color)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Trello labels: {str(e)}")
            raise
    
    def _create_label(self, color: str) -> str:
        """Create a label with the specified color on the board."""
        url = f"{self.base_url}/labels"
        params = {
            "key": self.api_key,
            "token": self.token,
            "idBoard": self.board_id,
            "name": color.capitalize(),
            "color": color
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            return response.json()["id"]
        except requests.exceptions.RequestException as e:
            print(f"Error creating Trello label: {str(e)}")
            raise
        
    def export_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Export tasks to Trello."""
        try:
            for task in tasks:
                # Ensure task has a title
                if not task.get("title"):
                    print("Skipping task with no title")
                    continue
                    
                # Create a card for the task
                card = self._create_card(task)
                print(f"Created Trello card: {card['shortUrl']}")
                
            return True
        except Exception as e:
            print(f"Error exporting to Trello: {str(e)}")
            raise

class ClickUpExporter(TaskExporter):
    """Export tasks to ClickUp."""
    
    def __init__(self, api_token: str = None, list_id: str = None, space_id: str = None):
        self.api_token = api_token or os.getenv("CLICKUP_API_TOKEN")
        self.list_id = list_id or os.getenv("CLICKUP_LIST_ID")
        self.space_id = space_id or os.getenv("CLICKUP_SPACE_ID")
        self.base_url = "https://api.clickup.com/api/v2"
        
        if not self.api_token:
            raise ValueError("ClickUp API token is required. Set CLICKUP_API_TOKEN environment variable.")
        
        # If no list ID is provided but a space ID is, get the first list in the space
        if not self.list_id and self.space_id:
            self.list_id = self._get_first_list_id()
        
        if not self.list_id:
            raise ValueError("ClickUp list ID is required. Either set CLICKUP_LIST_ID or provide a space ID.")
    
    def _get_first_list_id(self) -> str:
        """Get the ID of the first list in the space."""
        url = f"{self.base_url}/space/{self.space_id}/list"
        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            lists = response.json().get("lists", [])
            
            if lists:
                return lists[0]["id"]
            else:
                raise ValueError("No lists found in the specified ClickUp space")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching ClickUp lists: {str(e)}")
            raise
    
    def _create_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a ClickUp task."""
        url = f"{self.base_url}/list/{self.list_id}/task"
        
        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
        
        # Map priority to ClickUp priority format (1=Urgent, 2=High, 3=Normal, 4=Low)
        priority_map = {
            "High": 2,
            "Medium": 3,
            "Low": 4
        }
        
        # Map status to ClickUp status format
        status_map = {
            "To Do": "to do",
            "In Progress": "in progress",
            "Done": "complete"
        }
        
        # Convert due date to Unix timestamp if provided
        due_date = None
        if task.get("dueDate"):
            try:
                dt = datetime.fromisoformat(task["dueDate"].replace('Z', '+00:00'))
                due_date = int(dt.timestamp() * 1000)  # ClickUp uses milliseconds
            except (ValueError, TypeError):
                pass
        
        # Ensure description is not None before trying to append to it
        description = task.get("description", "") or ""
        
        # Prepare the request payload
        payload = {
            "name": task["title"],
            "description": description,
            "status": status_map.get(task.get("status", "To Do"), "to do"),
            "priority": priority_map.get(task.get("priority", "Medium"), 3)
        }
        
        # Add assignee if available - append to description instead of modifying it directly
        if task.get("assignee"):
            # In a real implementation, you'd need to resolve the assignee name to a ClickUp user ID
            # For now, we'll just add it to the description
            payload["description"] = f"{payload['description']}\n\nAssignee: {task['assignee']}".strip()
        
        # Add due date if available
        if due_date:
            payload["due_date"] = due_date
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating ClickUp task: {str(e)}")
            raise
        
    def export_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Export tasks to ClickUp."""
        try:
            for task in tasks:
                # Ensure task has a title
                if not task.get("title"):
                    print("Skipping task with no title")
                    continue
                    
                # Create a task in ClickUp
                clickup_task = self._create_task(task)
                print(f"Created ClickUp task: {clickup_task['id']}")
                
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
            # Ensure each task has a taskId
            for task in tasks:
                if "taskId" not in task or not task["taskId"]:
                    task["taskId"] = str(uuid.uuid4())
                    
                # Ensure each task has a createdAt timestamp
                if "createdAt" not in task or not task["createdAt"]:
                    task["createdAt"] = datetime.now().isoformat()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2)
            print(f"Tasks exported to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting tasks: {str(e)}")
            raise
            
    def _get_timestamp(self) -> str:
        """Get a timestamp string for the filename."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
