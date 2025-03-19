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

    def parse_messages_from_content(self, file_content):
        """
        Parse messages directly from file content string.
        
        Args:
            file_content: String containing the JSON content of the file
            
        Returns:
            List of processed messages
        """
        try:
            # Parse the JSON content
            messages_data = json.loads(file_content)
            
            # Process the messages
            processed_messages = []
            for msg in messages_data:
                if isinstance(msg, dict) and 'text' in msg:
                    # Extract username
                    if 'user_profile' in msg and 'real_name' in msg['user_profile']:
                        # Use the real name from user profile
                        username = msg['user_profile']['real_name']
                    else:
                        # Fall back to username or user ID
                        username = msg.get('username', msg.get('user', 'Unknown User'))
                    
                    processed_messages.append({
                        'username': username,
                        'message': msg.get('text', ''),
                        'timestamp': msg.get('ts', ''),
                        'user_profile': msg.get('user_profile', {})
                    })
            
            return processed_messages
        except json.JSONDecodeError:
            raise ValueError("The uploaded file is not a valid JSON file")
        except Exception as e:
            raise Exception(f"Error processing file content: {str(e)}")
