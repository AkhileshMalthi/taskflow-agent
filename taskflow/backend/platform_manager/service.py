"""
Platform Manager Service - Subscribes to extracted tasks and manages task creation.
For MVP, simulates task creation by logging to console and storing in memory.
"""

from taskflow.backend.config.logger import setup_logging, get_logger
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import asdict

from taskflow.backend.config.settings import config
from taskflow.backend.utils.messaging import MessageBroker, setup_taskflow_infrastructure
from taskflow.shared.events import TaskExtracted, TaskCreated, TaskFailed

logger = get_logger("taskflow.backend.platform_manager")


class MockPlatform:
    """Mock task platform for MVP demonstration."""
    
    def __init__(self, platform_name: str = "console"):
        """
        Initialize the mock platform.
        
        Args:
            platform_name: Name of the platform
        """
        self.platform_name = platform_name
        self.tasks: Dict[str, dict] = {}  # In-memory task storage
    
    def create_task(self, task: TaskExtracted) -> dict:
        """
        Create a task in the mock platform.
        
        Args:
            task: Task to create
            
        Returns:
            dict: Created task information
        """
        # Generate platform-specific task ID
        platform_task_id = f"{self.platform_name}_{uuid.uuid4().hex[:8]}"
        
        # Create task record
        task_record = {
            "platform_task_id": platform_task_id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "assigned_to": task.assigned_to,
            "labels": task.labels,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "platform": self.platform_name,
            "original_task_id": task.task_id
        }
        
        # Store in memory
        self.tasks[platform_task_id] = task_record
        
        # Log the task creation (MVP demo)
        self._log_task_creation(task_record)
        
        return task_record
    
    def _log_task_creation(self, task_record: dict):
        """Log task creation to console for MVP demonstration."""
        print("=" * 60)
        print("🎯 NEW TASK CREATED")
        print("=" * 60)
        print(f"Platform: {task_record['platform']}")
        print(f"Task ID: {task_record['platform_task_id']}")
        print(f"Title: {task_record['title']}")
        print(f"Description: {task_record['description']}")
        print(f"Priority: {task_record['priority']}")
        print(f"Due Date: {task_record['due_date'] or 'Not specified'}")
        print(f"Assigned To: {task_record['assigned_to'] or 'Unassigned'}")
        print(f"Labels: {', '.join(task_record['labels']) if task_record['labels'] else 'None'}")
        print(f"Created At: {task_record['created_at']}")
        print("=" * 60)
    
    def get_tasks(self) -> List[dict]:
        """Get all tasks from the platform."""
        return list(self.tasks.values())
    
    def get_task(self, platform_task_id: str) -> Optional[dict]:
        """Get a specific task by platform task ID."""
        return self.tasks.get(platform_task_id)


class PlatformManager:
    """Manages task creation across different platforms."""
    
    def __init__(self):
        """Initialize the platform manager."""
        self.platforms = {
            "console": MockPlatform("console"),
            "mock_trello": MockPlatform("mock_trello"),
            "mock_clickup": MockPlatform("mock_clickup")
        }
        self.default_platform = "console"
    
    def create_task(self, task: TaskExtracted, platform: Optional[str] = None) -> dict:
        """
        Create a task in the specified platform.
        
        Args:
            task: Task to create
            platform: Target platform (defaults to console)
            
        Returns:
            dict: Created task information
            
        Raises:
            ValueError: If platform is not supported
        """
        platform_name = platform or self.default_platform
        
        if platform_name not in self.platforms:
            raise ValueError(f"Unsupported platform: {platform_name}")
        
        platform_instance = self.platforms[platform_name]
        return platform_instance.create_task(task)
    
    def get_available_platforms(self) -> List[str]:
        """Get list of available platforms."""
        return list(self.platforms.keys())
    
    def get_all_tasks(self) -> Dict[str, List[dict]]:
        """Get all tasks from all platforms."""
        all_tasks = {}
        for platform_name, platform in self.platforms.items():
            all_tasks[platform_name] = platform.get_tasks()
        return all_tasks


class PlatformManagerService:
    """Service that manages task creation in various platforms."""
    
    def __init__(self, broker: MessageBroker):
        """
        Initialize the platform manager service.
        
        Args:
            broker: Connected MessageBroker instance
        """
        self.broker = broker
        self.platform_manager = PlatformManager()
    
    def start_consuming(self):
        """Start consuming extracted tasks and creating them in platforms."""
        logger.info("🏗️  Starting Platform Manager Service")
        
        def handle_task(routing_key: str, event: TaskExtracted):
            """Handle incoming task extraction events."""
            logger.info(f"Processing extracted task: {event.title} (ID: {event.task_id})")
            
            try:
                # Determine target platform (for MVP, use console)
                target_platform = "console"
                
                # Create task in platform
                created_task = self.platform_manager.create_task(event, target_platform)
                
                # Publish success event
                success_event = TaskCreated(
                    task_id=event.task_id,
                    platform=target_platform,
                    platform_task_id=created_task["platform_task_id"],
                    title=event.title,
                    created_at=datetime.now(),
                    platform_url=f"mock://{target_platform}/{created_task['platform_task_id']}",
                    metadata={
                        "original_source": event.metadata.get("source") if event.metadata else None,
                        "original_author": event.metadata.get("original_author") if event.metadata else None
                    }
                )
                
                self.broker.publish_event(
                    exchange_name=config.rabbitmq.exchange_name,
                    routing_key="task.created",
                    event=success_event
                )
                
                logger.info(f"✅ Task created successfully: {created_task['platform_task_id']}")
                
            except Exception as e:
                logger.error(f"Error creating task {event.task_id}: {e}")
                
                # Publish failure event
                failure_event = TaskFailed(
                    task_id=event.task_id,
                    platform="console",
                    title=event.title,
                    error_message=str(e),
                    failed_at=datetime.now(),
                    metadata={"original_task": asdict(event)}
                )
                
                self.broker.publish_event(
                    exchange_name=config.rabbitmq.exchange_name,
                    routing_key="task.failed",
                    event=failure_event
                )
        
        # Start consuming extracted tasks
        self.broker.consume_events("extracted_tasks", handle_task)


def create_platform_manager_service() -> PlatformManagerService:
    """
    Create and return a PlatformManagerService with a connected broker.
    
    Returns:
        PlatformManagerService: Ready-to-use platform manager service
    """
    broker = MessageBroker(
        host=config.rabbitmq.host,
        port=config.rabbitmq.port,
        username=config.rabbitmq.username,
        password=config.rabbitmq.password
    )
    
    broker.connect()
    setup_taskflow_infrastructure(broker)
    
    return PlatformManagerService(broker)


def run_platform_manager_service():
    """Run the platform manager service."""
    setup_logging()
    service = create_platform_manager_service()
    try:
        service.start_consuming()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down platform manager service...")
    finally:
        service.broker.disconnect()


if __name__ == "__main__":
    run_platform_manager_service()