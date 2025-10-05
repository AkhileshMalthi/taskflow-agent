"""
AI Task Extractor Service - Subscribes to messages and extracts tasks.
For MVP, uses simple rule-based extraction. Can be enhanced with LLM integration later.
"""

from taskflow.backend.config.logger import setup_logging, get_logger
from typing import List

from taskflow.backend.config.settings import config
from taskflow.backend.utils.messaging import MessageBroker, setup_taskflow_infrastructure
from taskflow.models.extractor import LLMResponse, Task
from taskflow.shared.events import MessageReceived, TaskExtracted
from taskflow.backend.utils.prompts import build_extraction_prompt_with_few_shots
from taskflow.backend.utils.llms import get_llm

logger = get_logger("taskflow.backend.extractor")


class TaskExtractor:
    """Simple rule-based task extractor for MVP."""
    
    def extract_tasks(self, message: MessageReceived) -> List[TaskExtracted]:
        """
        Extract tasks from a message using an LLM.
        Args:
            message: The message to analyze
        Returns:
            List[TaskExtracted]: List of extracted tasks
        """
        extracted_tasks = []

        # Get LLM from config
        llm = get_llm(config.llm.model_provider, config.llm.model_name)
        # Set structured output
        structured_llm = llm.with_structured_output(schema=LLMResponse)
        # Build prompt
        prompt = build_extraction_prompt_with_few_shots()

        # Run LLM
        try:
            response = structured_llm.invoke(
                prompt.format_messages(message=message.content)
            )
            
            if not isinstance(response, LLMResponse):
                logger.error("LLM response is not of type LLMResponse")
                return []
            
            for raw_task in response.tasks:
                task = Task(**raw_task.model_dump())
                extracted_tasks.append(
                    TaskExtracted(
                        task_id=task.task_id,
                        title=task.title,
                        description=task.description,
                        priority=task.priority,
                        due_date=task.due_date,
                        assigned_to=task.assigned_to,
                        labels=task.labels,
                        source_message_id=message.message_id,
                ))

            return extracted_tasks
        except Exception as e:
            logger.exception(f"LLM error: {e}")
            return []


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
    setup_logging()
    service = create_extractor_service()
    try:
        service.start_consuming()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down extractor service...")
    finally:
        service.broker.disconnect()


if __name__ == "__main__":
    run_extractor_service()