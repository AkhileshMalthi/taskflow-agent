# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Real platform integrations (Trello, ClickUp, Jira APIs)
- Live source integrations (Slack/Teams webhooks)
- React frontend with real-time WebSocket updates
- User authentication and multi-tenancy
- Advanced monitoring and observability
- Database migration system

---

## [0.1.0] - 2025-10-19

### Added
- **Event-Driven Architecture**: Complete RabbitMQ-based microservices architecture for async task processing
- **Message Ingestion Service**: CLI and web-based message submission with RabbitMQ publishing
- **AI Task Extraction Service**: LLM-powered task extraction supporting multiple providers:
  - Groq (default)
  - OpenAI
  - Anthropic
  - Google Gemini
- **Platform Manager Service**: Mock task creation service with console output (ready for real platform integration)
- **Streamlit Web Frontend**: Interactive web interface for message submission and task viewing
- **Service Orchestration**: Unified `run_service.py` script to run individual or all services
- **PostgreSQL Persistence Layer**:
  - Database models for tasks and messages using SQLAlchemy ORM
  - CRUD operations for creating and querying data
  - UUID-based primary keys for distributed system support
  - JSONB support for flexible metadata storage
- **Configuration Management**:
  - Environment-based settings via `.env` file
  - Centralized logging configuration with customizable log levels
  - Support for multiple LLM providers and models
- **Event Schemas**: Pydantic-based event models for type-safe message passing:
  - `MessageReceived`: Conversation messages from various sources
  - `TaskExtracted`: Tasks extracted by AI service
  - `TaskCreated`: Successfully created tasks
  - `TaskFailed`: Failed task creation events
- **Comprehensive Documentation**:
  - Complete README with architecture diagrams
  - Quick start guide with multiple installation methods
  - Service architecture documentation with SVG diagrams
  - API usage examples and configuration guide
- **Testing Infrastructure**:
  - Pytest configuration with proper test paths
  - Unit tests for task extraction service with LLM mocking
  - Editable package installation support (`pip install -e .`)
- **Build System**: Hatchling-based build configuration for package distribution
- **MIT License**: Open source licensing for community use and contribution

### Changed
- Migrated from manual task extraction to LLM-powered AI extraction
- Consolidated PostgreSQL settings into single `DATABASE_URL` configuration
- Replaced individual logging setup with centralized logger configuration across all services
- Updated project title to "Taskflow Agent 2.0" to reflect event-driven architecture

### Fixed
- Test imports now work correctly with editable package installation
- Package can be properly installed and imported as `taskflow` module

### Technical Details

#### Architecture
```
[Ingestor Service] ---(RabbitMQ)---> [AI Task Extractor] ---(RabbitMQ)---> [Platform Manager]
        |                                     |                                    |
   Message Input                        Task Extraction                    Task Creation
    (CLI/Web UI)                        (LLM-powered AI)                 (Console/Mock)
```

#### Dependencies
- Python 3.11+
- RabbitMQ 4.x for message brokering
- PostgreSQL for data persistence
- LangChain for LLM integration
- Streamlit for web interface
- SQLAlchemy for ORM
- Pika for RabbitMQ client

#### Database Schema
- **Messages Table**: Stores incoming conversation messages with metadata
- **Tasks Table**: Stores extracted tasks with relationships to source messages

---

## Notes

### Version 0.1.0 Limitations
- Platform integrations are mocked (no real Trello/ClickUp/Jira creation)
- No real-time source integrations (Slack/Teams webhooks not implemented)
- Basic web UI (no advanced features like filtering, search, or dashboards)
- Minimal test coverage (contributions welcome!)
- No database migration system
- No user authentication or authorization

### Breaking Changes
N/A - This is the initial release

---

[Unreleased]: https://github.com/AkhileshMalthi/taskflow-agent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/AkhileshMalthi/taskflow-agent/releases/tag/v0.1.0
