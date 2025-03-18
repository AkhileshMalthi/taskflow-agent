import json
from typing import List, Dict, Any
import os
import datetime

class SlackMessageProcessor:
    """Processes Slack messages for task extraction."""
    
    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv("SLACK_API_TOKEN")
        
    def load_messages_from_file(self, channel: str, date: str = None) -> List[Dict[str, Any]]:
        """Load messages from a JSON file for a specific channel and date."""
        if date is None:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
            
        filepath = f"d:\\Projects\\taskflow-agent\\data\\{channel}\\{date}.json"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                return self._format_messages(messages)
        except FileNotFoundError:
            # Create an empty messages file if not found
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump([], f)
            print(f"No messages found for channel {channel} on {date}. Created empty file.")
            return []
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in messages file: {e}")
        except Exception as e:
            raise Exception(f"Error loading messages: {str(e)}")
            
    def _format_messages(self, raw_messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Convert raw Slack message format to simplified format for processing."""
        formatted_messages = []
        
        try:
            for msg in raw_messages:
                if 'user_profile' in msg and 'text' in msg and msg['type'] == 'message':
                    formatted_messages.append({
                        "username": msg['user_profile'].get('real_name', 'Unknown User'),
                        "message": msg['text']
                    })
        except Exception as e:
            raise ValueError(f"Error formatting messages: {str(e)}")
                
        return formatted_messages
