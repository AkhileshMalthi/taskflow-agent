from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load LLM using API key from environment
llm = ChatGroq(model="groq/mixtral-8x7b-32768", api_key=os.getenv("GROQ_API_KEY"))

# 1️⃣ Conversation Filtering Agent
filtering_agent = Agent(
    role="Task Filter",
    goal="Identify messages that contain task-related information.",
    backstory="You are an AI that filters Slack messages, keeping only those related to task assignments, deadlines, or work requests.",
    llm=llm
)

filtering_task = Task(
    description="""
    Review the provided Slack messages and identify only those that contain task-related information.
    Task-related messages typically include:
    - Work assignments (e.g., "Can you fix this?", "Please implement this")
    - Deadlines (e.g., "by tomorrow", "next week")
    - Commitments to do something (e.g., "I'll work on this")
    
    Here are the messages to filter:
    {messages}
    
    Return only the messages that contain task information and explain why you kept each one.
    """,
    expected_output="A list of filtered messages containing only task-related information with explanations.",
    agent=filtering_agent
)

# 2️⃣ Task Extraction Agent
extraction_agent = Agent(
    role="Task Extractor",
    goal="Extract specific task details from messages.",
    backstory="You analyze task-related messages and extract structured information about what needs to be done, by whom, and by when.",
    llm=llm
)

extraction_task = Task(
    description="""
    Analyze these filtered task-related messages and extract structured task information.
    For each message, identify:
    1. Task title/description (what needs to be done)
    2. Assignee (who is responsible)
    3. Deadline (when it's due)
    
    Return a list of structured tasks, each with title, assignee, and deadline fields.
    """,
    expected_output="A list of structured task objects with title, assignee, and deadline fields.",
    agent=extraction_agent,
    depends_on=[filtering_task]
)

# 3️⃣ Task Formatting Agent
formatting_agent = Agent(
    role="Task Formatter",
    goal="Format extracted tasks into a standard JSON format.",
    backstory="You transform raw task data into properly formatted JSON that can be imported into task management systems.",
    llm=llm
)

formatting_task = Task(
    description="""
    Take the extracted task details and format them into a consistent JSON structure.
    Each task should follow this format:
    {{
      "title": "Task description",
      "assignee": "Person responsible or null if unspecified",
      "dueDate": "ISO format date or null if unspecified"
    }}
    
    Format dates in ISO format (YYYY-MM-DDThh:mm:ss.sssZ) when possible.
    Return a valid JSON array containing all formatted tasks.
    """,
    expected_output="A JSON array of properly formatted task objects ready for import.",
    agent=formatting_agent,
    depends_on=[extraction_task]
)

# Crew Orchestration
crew = Crew(
    agents=[filtering_agent, extraction_agent, formatting_agent],
    tasks=[filtering_task, extraction_task, formatting_task],
    verbose=True,  # Enable verbose output to see what's happening
    process="sequential"  # Use string value
)

# Function to Process Messages
slack_messages = [
    {"username": "John", "message": "@Alice Can you fix the login issue by tomorrow?"},
    {"username": "Mike", "message": "Hey, how's your day?"},
    {"username": "Alice", "message": "I'll implement the new API feature next week."}
]

def process_messages(messages):
    result = crew.kickoff(inputs={"messages": messages})
    return result

# Run Extraction
tasks_json = process_messages(slack_messages)
print(tasks_json)
