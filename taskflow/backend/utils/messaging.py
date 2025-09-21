"""
RabbitMQ messaging utility for event-driven communication between services.
Provides publish and consume functionality with automatic connection management.
"""

import json
import logging
import pika
from typing import Callable, Optional, Any
from pika.adapters.blocking_connection import BlockingConnection, BlockingChannel

from taskflow.shared.events import serialize_event, deserialize_event

logger = logging.getLogger(__name__)


class MessageBroker:
    """Handles RabbitMQ connections and messaging operations."""
    
    def __init__(self, host: str = "localhost", port: int = 5672, 
                 username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the message broker.
        
        Args:
            host: RabbitMQ server host
            port: RabbitMQ server port
            username: Optional username for authentication
            password: Optional password for authentication
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection: Optional[BlockingConnection] = None
        self.channel: Optional[BlockingChannel] = None
        
    def connect(self) -> None:
        """Establish connection to RabbitMQ server with retry logic."""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                if self.username and self.password:
                    credentials = pika.PlainCredentials(self.username, self.password)
                    parameters = pika.ConnectionParameters(
                        host=self.host,
                        port=self.port,
                        credentials=credentials,
                        heartbeat=600,  # Increase heartbeat
                        blocked_connection_timeout=300,  # Connection timeout
                    )
                else:
                    parameters = pika.ConnectionParameters(
                        host=self.host,
                        port=self.port,
                        heartbeat=600,  # Increase heartbeat
                        blocked_connection_timeout=300,  # Connection timeout
                    )
                
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
                return
                
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to RabbitMQ after {max_retries} attempts")
                    raise
    
    def disconnect(self) -> None:
        """Close connection to RabbitMQ server."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Disconnected from RabbitMQ")
    
    def declare_exchange(self, exchange_name: str, exchange_type: str = "topic") -> None:
        """
        Declare an exchange.
        
        Args:
            exchange_name: Name of the exchange
            exchange_type: Type of exchange (topic, direct, fanout, headers)
        """
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")
        
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True
        )
        logger.debug(f"Declared exchange: {exchange_name} ({exchange_type})")
    
    def declare_queue(self, queue_name: str, durable: bool = True) -> None:
        """
        Declare a queue.
        
        Args:
            queue_name: Name of the queue
            durable: Whether the queue should survive server restarts
        """
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")
        
        self.channel.queue_declare(queue=queue_name, durable=durable)
        logger.debug(f"Declared queue: {queue_name}")
    
    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str) -> None:
        """
        Bind a queue to an exchange with a routing key.
        
        Args:
            queue_name: Name of the queue
            exchange_name: Name of the exchange
            routing_key: Routing key pattern
        """
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")
        
        self.channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        logger.debug(f"Bound queue {queue_name} to exchange {exchange_name} with key {routing_key}")
    
    def publish_event(self, exchange_name: str, routing_key: str, event: Any) -> None:
        """
        Publish an event to an exchange with auto-reconnection.
        
        Args:
            exchange_name: Name of the exchange
            routing_key: Routing key for the message
            event: Event object to publish
        """
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                # Check if we need to reconnect
                if (not self.channel or not self.connection or 
                    self.connection.is_closed or self.channel.is_closed):
                    logger.warning("Connection lost, attempting to reconnect...")
                    self.connect()
                
                if not self.channel:
                    raise RuntimeError("Failed to establish channel")
                
                message_body = serialize_event(event)
                
                self.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key=routing_key,
                    body=message_body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Make message persistent
                        content_type="application/json"
                    )
                )
                
                logger.info(f"Published event {event.event_type} to {exchange_name}/{routing_key}")
                return
                
            except Exception as e:
                error_str = str(e)
                if any(x in error_str.lower() for x in ['connection', 'channel', 'closed', 'reset']):
                    logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        try:
                            self.connect()
                        except Exception as reconnect_error:
                            logger.error(f"Reconnection failed: {reconnect_error}")
                    else:
                        logger.error(f"Failed to publish event after {max_retries} attempts")
                        raise
                else:
                    logger.error(f"Failed to publish event: {e}")
                    raise
    
    def consume_events(self, queue_name: str, callback: Callable[[str, Any], None]) -> None:
        """
        Start consuming events from a queue.
        
        Args:
            queue_name: Name of the queue to consume from
            callback: Function to call for each received message
                      Should accept (routing_key, event_object) parameters
        """
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")
        
        def wrapper(ch, method, properties, body):
            try:
                # Deserialize the event
                message_data = json.loads(body.decode('utf-8'))
                event_type = message_data.get('event_type')
                
                if not event_type:
                    logger.error("Received message without event_type")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    return
                
                event = deserialize_event(body.decode('utf-8'), event_type)
                
                # Call the user-provided callback
                callback(method.routing_key, event)
                
                # Acknowledge the message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                # Reject and don't requeue the message
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapper
        )
        
        logger.info(f"Started consuming from queue: {queue_name}")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumption...")
            self.channel.stop_consuming()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Convenience functions for common operations
def create_broker(host: str = "localhost", port: int = 5672, 
                 username: Optional[str] = None, password: Optional[str] = None) -> MessageBroker:
    """Create and return a MessageBroker instance."""
    return MessageBroker(host=host, port=port, username=username, password=password)


def setup_taskflow_infrastructure(broker: MessageBroker) -> None:
    """
    Set up the standard exchanges, queues, and bindings for taskflow.
    
    Args:
        broker: Connected MessageBroker instance
    """
    # Declare main exchange
    broker.declare_exchange("taskflow", "topic")
    
    # Declare queues
    broker.declare_queue("conversation_messages")
    broker.declare_queue("extracted_tasks")
    broker.declare_queue("task_results")
    
    # Bind queues to exchange
    broker.bind_queue("conversation_messages", "taskflow", "conversation.*")
    broker.bind_queue("extracted_tasks", "taskflow", "task.extracted")
    broker.bind_queue("task_results", "taskflow", "task.created")
    broker.bind_queue("task_results", "taskflow", "task.failed")
    
    logger.info("Taskflow messaging infrastructure set up successfully")