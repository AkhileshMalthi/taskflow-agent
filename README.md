# Taskflow Agent (Event-Driven, RabbitMQ Edition)

## Vision
A scalable service that automatically creates actionable tasks from real-time conversations, using an event-driven architecture. The system ingests messages, uses AI to extract tasks, and exports them to the user's desired platform (Trello, ClickUp, etc.).

---

## Architecture Overview

- **Ingestor Service**: Collects and normalizes messages from various sources (e.g., Slack, Teams).
- **AI Task Extractor Service**: Subscribes to message events, extracts tasks using AI, and emits task events.
- **Task Platform Manager Service**: Subscribes to task events and creates tasks in the user's chosen platform.
- **Event Bus**: RabbitMQ is used for all inter-service communication.

---

## Event Flow

1. **Ingestor** publishes `conversation.message_received` events.
2. **AI Task Extractor** subscribes to `conversation.message_received`, extracts tasks, and publishes `task.extracted` events.
3. **Task Platform Manager** subscribes to `task.extracted`, creates tasks in the platform, and publishes `task.created` or `task.failed` events.

---

## Next Steps

1. **Set up project structure**
    - `ingestor/` (service)
    - `extractor/` (service)
    - `platform_manager/` (service)
    - `utils/` (shared code, e.g., messaging)
    - `config/` (settings, .env)
2. **Add RabbitMQ dependency** (`pika`)
3. **Implement messaging utility** for publish/subscribe
4. **Implement Ingestor Service** (publishes messages)
5. **Implement AI Task Extractor Service** (subscribes to messages, publishes tasks)
6. **Implement Task Platform Manager Service** (subscribes to tasks, creates tasks in platform)
7. **Add event schemas and documentation**
8. **Add logging and error handling**
9. **Write integration tests**
10. **Document everything in README**

---

## Requirements
- Python 3.9+
- RabbitMQ (local or cloud instance)
- `pika` Python package

---

## Getting Started
1. Clone the repo
2. Set up RabbitMQ
3. Install dependencies: `pip install -r requirements.txt`
4. Run each service in a separate terminal

---

## License
MIT
