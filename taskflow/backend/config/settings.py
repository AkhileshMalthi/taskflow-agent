"""
Configuration management for the taskflow application.
Handles environment variables and application settings.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class RabbitMQConfig:
    """RabbitMQ connection configuration."""
    host: str = "localhost"
    port: int = 5672
    username: Optional[str] = None
    password: Optional[str] = None
    exchange_name: str = "taskflow"

@dataclass
class LLMConfig:
    """Configuration for Language Model."""
    model_provider: str = "groq"
    model_name: str = "llama-3.3-70b-versatile"

@dataclass
class AppConfig:
    """Main application configuration."""
    rabbitmq: RabbitMQConfig
    llm: LLMConfig
    log_level: str = "INFO"
    service_name: str = "taskflow"


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.
    
    Returns:
        AppConfig: Loaded configuration
    """
    rabbitmq_config = RabbitMQConfig(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        username=os.getenv("RABBITMQ_USERNAME"),
        password=os.getenv("RABBITMQ_PASSWORD"),
        exchange_name=os.getenv("RABBITMQ_EXCHANGE", "taskflow")
    )

    llm_config = LLMConfig(
        model_provider=os.getenv("TASKFLOW_MODEL_PROVIDER", "groq"),
        model_name=os.getenv("TASKFLOW_MODEL_NAME", "llama-3.3-70b-versatile")
    )

    return AppConfig(
        rabbitmq=rabbitmq_config,
        llm=llm_config,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        service_name=os.getenv("SERVICE_NAME", "taskflow")
    )


# Global config instance
config = load_config()