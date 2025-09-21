"""
Ingestor Service - Accepts messages and publishes conversation.message_received events.
For MVP, this provides a simple interface to submit messages manually.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from taskflow.backend.config.settings import config
from taskflow.backend.utils.messaging import MessageBroker, setup_taskflow_infrastructure
from taskflow.shared.events import MessageReceived

logger = logging.getLogger(__name__)


class IngestorService:
    """Service that ingests messages and publishes them as events."""
    
    def __init__(self, broker: MessageBroker):
        """
        Initialize the ingestor service.
        
        Args:
            broker: Connected MessageBroker instance
        """
        self.broker = broker
        
    def ingest_message(self, content: str, author: str, source: str = "manual", 
                      channel: Optional[str] = None, metadata: Optional[dict] = None) -> str:
        """
        Ingest a message and publish it as an event.
        
        Args:
            content: The message content
            author: Author of the message
            source: Source of the message (e.g., "slack", "teams", "manual")
            channel: Optional channel/room name
            metadata: Optional additional metadata
            
        Returns:
            str: The generated message ID
        """
        # Generate unique message ID
        message_id = str(uuid.uuid4())
        
        # Create the event
        event = MessageReceived(
            message_id=message_id,
            source=source,
            content=content,
            author=author,
            timestamp=datetime.now(),
            channel=channel,
            metadata=metadata or {}
        )
        
        # Publish the event
        try:
            self.broker.publish_event(
                exchange_name=config.rabbitmq.exchange_name,
                routing_key="conversation.message_received",
                event=event
            )
            
            logger.info(f"Ingested message {message_id} from {author} ({source})")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to ingest message: {e}")
            raise
    
    def ingest_batch(self, messages: list) -> list[str]:
        """
        Ingest multiple messages in batch.
        
        Args:
            messages: List of message dictionaries with keys: content, author, source, etc.
            
        Returns:
            list[str]: List of generated message IDs
        """
        message_ids = []
        
        for msg in messages:
            try:
                message_id = self.ingest_message(
                    content=msg.get("content", ""),
                    author=msg.get("author", ""),
                    source=msg.get("source", "manual"),
                    channel=msg.get("channel"),
                    metadata=msg.get("metadata")
                )
                message_ids.append(message_id)
                
            except Exception as e:
                logger.error(f"Failed to ingest message in batch: {e}")
                # Continue with other messages
                continue
        
        logger.info(f"Ingested {len(message_ids)} messages in batch")
        return message_ids


def create_ingestor_service() -> IngestorService:
    """
    Create and return an IngestorService with a connected broker.
    
    Returns:
        IngestorService: Ready-to-use ingestor service
    """
    broker = MessageBroker(
        host=config.rabbitmq.host,
        port=config.rabbitmq.port,
        username=config.rabbitmq.username,
        password=config.rabbitmq.password
    )
    
    broker.connect()
    setup_taskflow_infrastructure(broker)
    
    return IngestorService(broker)


def run_ingestor_cli():
    """
    Run the ingestor service in CLI mode for testing.
    Allows manual message input for demonstration purposes.
    """
    logging.basicConfig(level=getattr(logging, config.log_level))
    
    print("🚀 Starting Taskflow Ingestor Service (CLI Mode)")
    print("Type messages to ingest them. Type 'quit' to exit.\n")
    
    service = create_ingestor_service()
    
    try:
        while True:
            # Get user input
            content = input("Message content: ").strip()
            
            if content.lower() == 'quit':
                break
                
            if not content:
                continue
            
            author = input("Author (default: user): ").strip() or "user"
            channel = input("Channel (optional): ").strip() or None
            
            try:
                message_id = service.ingest_message(
                    content=content,
                    author=author,
                    source="cli",
                    channel=channel
                )
                
                print(f"✅ Ingested message: {message_id}\n")
                
            except Exception as e:
                print(f"❌ Error ingesting message: {e}\n")
    
    except KeyboardInterrupt:
        print("\n👋 Shutting down ingestor service...")
    
    finally:
        service.broker.disconnect()


if __name__ == "__main__":
    run_ingestor_cli()