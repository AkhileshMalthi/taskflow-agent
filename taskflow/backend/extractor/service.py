"""
AI Task Extractor Service - Subscribes to messages and extracts tasks.
For MVP, uses simple rule-based extraction. Can be enhanced with LLM integration later.
"""

import logging
import re
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from taskflow.backend.config.settings import config
from taskflow.backend.utils.messaging import MessageBroker, setup_taskflow_infrastructure
from taskflow.shared.events import MessageReceived, TaskExtracted

logger = logging.getLogger(__name__)


class TaskExtractor:
    """Simple rule-based task extractor for MVP."""
    
    # Task indicators - words/phrases that suggest actionable tasks
    TASK_INDICATORS = [
        r'\b(?:need to|have to|must|should|todo|action item|task|assign|delegate)\b',
        r'\b(?:please|can you|could you|would you)\b.*\b(?:do|create|make|build|fix|update|check)\b',
        r'\b(?:let\'s|we need to|we should|someone should)\b',
        r'@\w+.*\b(?:please|can you|could you)\b',  # @ mentions with requests
    ]
    
    # Priority indicators
    HIGH_PRIORITY = [r'\b(?:urgent|asap|immediately|critical|high priority)\b']
    MEDIUM_PRIORITY = [r'\b(?:soon|important|medium priority)\b']
    
    # Due date patterns
    DUE_DATE_PATTERNS = [
        r'\b(?:by|due|deadline|before)\s+(\w+day|\d{1,2}[\/\-]\d{1,2}|\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\b',
        r'\b(?:in|within)\s+(\d+)\s+(days?|weeks?|months?)\b',
        r'\b(today|tomorrow|next week|next month)\b'
    ]
    
    # Assignee patterns
    ASSIGNEE_PATTERNS = [
        r'@(\w+)',  # @username mentions
        r'\b(?:assign to|assigned to|for)\s+(\w+)\b'
    ]

    def extract_tasks(self, message: MessageReceived) -> List[TaskExtracted]:
        """
        Extract tasks from a message using rule-based approach.
        
        Args:
            message: The message to analyze
            
        Returns:
            List[TaskExtracted]: List of extracted tasks
        """
        tasks = []
        content = message.content.lower()
        
        # Check if message contains task indicators
        if not self._contains_task_indicators(content):
            return tasks
        
        # For MVP, create one task per message that matches patterns
        # In a real implementation, you might split messages into multiple tasks
        task = self._create_task_from_message(message)
        if task:
            tasks.append(task)
        
        return tasks
    
    def _contains_task_indicators(self, content: str) -> bool:
        """Check if content contains task indicators."""
        for pattern in self.TASK_INDICATORS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def _create_task_from_message(self, message: MessageReceived) -> Optional[TaskExtracted]:
        """Create a task from a message."""
        try:
            # Generate task ID
            task_id = str(uuid.uuid4())
            
            # Extract task title (first sentence or up to 100 chars)
            title = self._extract_title(message.content)
            
            # Extract priority
            priority = self._extract_priority(message.content)
            
            # Extract due date
            due_date = self._extract_due_date(message.content)
            
            # Extract assignee
            assigned_to = self._extract_assignee(message.content)
            
            # Create task
            task = TaskExtracted(
                task_id=task_id,
                source_message_id=message.message_id,
                title=title,
                description=message.content,
                priority=priority,
                due_date=due_date,
                assigned_to=assigned_to,
                labels=["auto-extracted"],
                metadata={
                    "source": message.source,
                    "channel": message.channel,
                    "original_author": message.author
                }
            )
            
            return task
            
        except Exception as e:
            logger.error(f"Error creating task from message {message.message_id}: {e}")
            return None
    
    def _extract_title(self, content: str) -> str:
        """Extract a concise title from message content."""
        # Remove common prefixes
        content = re.sub(r'^\s*(?:hey|hi|hello|please|can you|could you|we need to|let\'s)\s*', '', content, flags=re.IGNORECASE)
        
        # Get first sentence or first 80 characters
        sentences = re.split(r'[.!?]', content)
        if sentences:
            title = sentences[0].strip()
            if len(title) > 80:
                title = title[:77] + "..."
            return title
        
        return content[:80] + "..." if len(content) > 80 else content
    
    def _extract_priority(self, content: str) -> str:
        """Extract priority from content."""
        content_lower = content.lower()
        
        for pattern in self.HIGH_PRIORITY:
            if re.search(pattern, content_lower):
                return "high"
        
        for pattern in self.MEDIUM_PRIORITY:
            if re.search(pattern, content_lower):
                return "medium"
        
        return "low"
    
    def _extract_due_date(self, content: str) -> Optional[datetime]:
        """Extract due date from content."""
        content_lower = content.lower()
        
        # Look for specific date patterns
        for pattern in self.DUE_DATE_PATTERNS:
            match = re.search(pattern, content_lower)
            if match:
                date_text = match.group(0)
                
                # Simple date parsing for MVP
                if "today" in date_text:
                    return datetime.now().replace(hour=23, minute=59, second=59)
                elif "tomorrow" in date_text:
                    return (datetime.now() + timedelta(days=1)).replace(hour=23, minute=59, second=59)
                elif "next week" in date_text:
                    return (datetime.now() + timedelta(weeks=1)).replace(hour=23, minute=59, second=59)
                elif "next month" in date_text:
                    return (datetime.now() + timedelta(days=30)).replace(hour=23, minute=59, second=59)
        
        return None
    
    def _extract_assignee(self, content: str) -> Optional[str]:
        """Extract assignee from content."""
        for pattern in self.ASSIGNEE_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None


class ExtractorService:
    """Service that extracts tasks from messages."""
    
    def __init__(self, broker: MessageBroker):
        """
        Initialize the extractor service.
        
        Args:
            broker: Connected MessageBroker instance
        """
        self.broker = broker
        self.extractor = TaskExtractor()
    
    def start_consuming(self):
        """Start consuming messages and extracting tasks."""
        logger.info("🤖 Starting AI Task Extractor Service")
        
        def handle_message(routing_key: str, event: MessageReceived):
            """Handle incoming message events."""
            logger.info(f"Processing message {event.message_id} from {event.author}")
            
            try:
                # Extract tasks from the message
                tasks = self.extractor.extract_tasks(event)
                
                if not tasks:
                    logger.info(f"No tasks extracted from message {event.message_id}")
                    return
                
                # Publish extracted tasks
                for task in tasks:
                    self.broker.publish_event(
                        exchange_name=config.rabbitmq.exchange_name,
                        routing_key="task.extracted",
                        event=task
                    )
                    
                    logger.info(f"✅ Extracted task: {task.title} (ID: {task.task_id})")
                
            except Exception as e:
                logger.error(f"Error processing message {event.message_id}: {e}")
        
        # Start consuming messages
        self.broker.consume_events("conversation_messages", handle_message)


def create_extractor_service() -> ExtractorService:
    """
    Create and return an ExtractorService with a connected broker.
    
    Returns:
        ExtractorService: Ready-to-use extractor service
    """
    broker = MessageBroker(
        host=config.rabbitmq.host,
        port=config.rabbitmq.port,
        username=config.rabbitmq.username,
        password=config.rabbitmq.password
    )
    
    broker.connect()
    setup_taskflow_infrastructure(broker)
    
    return ExtractorService(broker)


def run_extractor_service():
    """Run the extractor service."""
    logging.basicConfig(level=getattr(logging, config.log_level))
    
    service = create_extractor_service()
    
    try:
        service.start_consuming()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down extractor service...")
    finally:
        service.broker.disconnect()


if __name__ == "__main__":
    run_extractor_service()