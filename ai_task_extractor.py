import os
import logging
from typing import List, Dict
import json

logger = logging.getLogger(__name__)

class AITaskExtractor:
    """Extracts tasks from conversations using AI models."""
    
    def __init__(self):
        self.groq_api_key = os.environ.get('GROQ_API_KEY')
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    def process_conversation(self, messages: List[Dict]) -> List[Dict]:
        """
        Process a conversation and extract tasks using AI.
        
        This is a stub implementation. In production, this would use Groq or OpenAI APIs.
        
        Args:
            messages: List of message dictionaries with user and text keys
            
        Returns:
            List of task dictionaries
        """
        logger.info(f"Processing {len(messages)} messages for task extraction")
        
        # For now, return mock tasks based on simple keyword matching
        potential_tasks = []
        
        for message in messages:
            text = message.get('text', '').lower()
            user = message.get('user', '')
            
            # Very simple keyword detection
            if any(keyword in text for keyword in ['todo', 'task', 'assignment', 'deadline']):
                # Extract simple tasks for testing
                if 'create' in text or 'make' in text or 'do' in text:
                    task_title = text.split('do')[-1].strip() if 'do' in text else text
                    
                    potential_tasks.append({
                        'title': task_title[:50],  # Limit title length
                        'description': text,
                        'assigned_to': user,  # Default to the message author
                        'priority': 'medium'
                    })
        
        logger.info(f"Extracted {len(potential_tasks)} potential tasks")
        return potential_tasks