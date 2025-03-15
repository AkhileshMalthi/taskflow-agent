from typing import List, Dict, Optional
import logging
from datetime import datetime
from ai_task_extractor import AITaskExtractor

logger = logging.getLogger(__name__)

class ConversationHandler:
    """Handles conversation analysis for task extraction."""
    
    def __init__(self):
        self.is_recording = False
        self.current_conversation = []
        self.ai_extractor = AITaskExtractor()
        self.logger = logger

    def start_recording(self) -> None:
        """Start recording the conversation."""
        self.is_recording = True
        self.current_conversation = []
        logger.info("Started recording conversation")

    def stop_recording(self) -> None:
        """Stop recording the conversation."""
        self.is_recording = False
        logger.info("Stopped recording conversation")

    def add_message(self, user_id: str, text: str) -> None:
        """Add a message to the current conversation."""
        if self.is_recording:
            self.current_conversation.append({
                "user": user_id,
                "text": text,
                "timestamp": datetime.utcnow().isoformat()
            })

    def extract_potential_tasks(self) -> List[Dict]:
        """Extract potential tasks from the recorded conversation using AI."""
        try:
            if not self.current_conversation:
                return []

            # Use AI to extract tasks from conversation
            tasks = self.ai_extractor.process_conversation(self.current_conversation)

            # Add conversation context to each task
            for task in tasks:
                task['context'] = self._get_message_context(
                    self._find_message_index(task['title'])
                )

            return tasks

        except Exception as e:
            logger.error(f"Error extracting tasks: {e}")
            return []

    def _find_message_index(self, search_text: str) -> int:
        """Find the index of a message containing specific text."""
        for i, message in enumerate(self.current_conversation):
            if search_text.lower() in message['text'].lower():
                return i
        return 0

    def _get_message_context(self, message_index: int, context_window: int = 2) -> List[Dict]:
        """Get the context messages around a specific message."""
        start = max(0, message_index - context_window)
        end = min(len(self.current_conversation), message_index + context_window + 1)
        return self.current_conversation[start:end]

    def extract_potential_tasks(self, messages):
        """
        Extract potential tasks from conversation messages.
        
        Args:
            messages (list): List of message dicts with user and text keys
            
        Returns:
            list: List of potential task dictionaries
        """
        self.logger.info(f"Extracting tasks from {len(messages)} messages")
        
        # In a real implementation, this would use LLM to analyze messages
        # For now, we'll return a mock task if we see certain keywords
        
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
        
        self.logger.info(f"Extracted {len(potential_tasks)} potential tasks")
        return potential_tasks