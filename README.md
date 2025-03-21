# TaskFlow Agent

TaskFlow Agent is an AI-powered tool that automatically extracts and manages tasks from conversations. It analyzes Slack conversations, identifies task-related messages, and can export them to popular task management platforms like Trello and ClickUp.

## Features

- **Automatic Task Extraction**: Identifies task assignments, deadlines, and responsibilities in conversations
- **Intelligent Parsing**: Extracts key task details including title, description, assignee, due date, and priority
- **Multiple Integrations**:
  - **Slack**: Processes messages from Slack exported conversation data (JSON format)
  - **Trello**: Exports tasks as cards with appropriate labels and details
  - **ClickUp**: Creates tasks with priorities, descriptions, and deadlines
- **Flexible Export Options**: Save tasks as JSON or send directly to task management platforms
- **Interactive UI**: Built with Streamlit for easy configuration and visualization
- **File Management**: Save and reload conversation files for future analysis

## Quick Start

1. **Setup Environment**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/taskflow-agent.git
   cd taskflow-agent
   
   # Create and activate virtual environment
   python -m venv .agentenv
   source .agentenv/bin/activate  # On Windows: .agentenv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   Create a `.env` file with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key
   LLM_MODEL=groq/mixtral-8x7b-32768
   TRELLO_API_KEY=your_trello_api_key
   TRELLO_API_TOKEN=your_trello_token
   TRELLO_BOARD_ID=your_trello_board_id
   TRELLO_LIST_ID=your_trello_list_id
   CLICKUP_API_TOKEN=your_clickup_token
   CLICKUP_LIST_ID=your_clickup_list_id
   CLICKUP_SPACE_ID=your_clickup_space_id
   ```

   Alternatively, you can configure these through the UI after launching the application.

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## How It Works

TaskFlow Agent uses a series of AI agents powered by CrewAI, each specializing in a specific part of the task extraction process:

1. **Filtering Agent**: Identifies which messages contain task-related information
2. **Extraction Agent**: Extracts structured task data from the filtered messages
3. **Formatting Agent**: Formats the extracted tasks into a standardized JSON structure

These agents work in sequence, passing information to each other through a process orchestrated by CrewAI.

## User Interface

The Streamlit-based UI provides:
- File upload for Slack conversation JSON files
- Saved file management (save, load, delete)
- Configuration interface for API credentials
- Task extraction and visualization
- Export options to different platforms

## Data Format

Tasks are extracted in the following format:

```json
{
  "title": "Task title",
  "description": "Detailed description",
  "assignee": "Person responsible",
  "dueDate": "2023-04-01T12:00:00.000Z",
  "priority": "High",
  "status": "To Do",
  "createdAt": "2023-03-28T15:30:45.123Z",
  "taskId": "unique-task-id"
}
```

## Project Structure

- `agents/`: Agent definitions for each specialized task
- `tasks/`: Task definitions that provide instructions to the agents
- `integrations/`: Integration code for Slack, Trello, and ClickUp
- `prompts/`: Templates for agent instructions
- `utils/`: Utility functions including configuration management
- `data/`: Directory for saved conversation files
- `app.py`: Main Streamlit application
- `config.py`: Configuration class for environment variables

## Requirements

- Python 3.11+
- CrewAI
- LangChain
- Groq API Access
- Streamlit
- Requests (for API integrations)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
