import streamlit as st
from crewai import Crew
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import json

from config import Config
from agents.filtering_agent import FilteringAgent
from agents.task_extraction_agent import TaskExtractionAgent
from agents.task_formatting_agent import TaskFormattingAgent
from tasks.filtering_task import FilteringTask
from tasks.extraction_task import ExtractionTask
from tasks.formatting_task import FormattingTask
from integrations.slack_processor import SlackMessageProcessor

# Load environment variables
load_dotenv()
config = Config.from_env()

def initialize_llm():
    """Initialize the language model."""
    return ChatGroq(model=config.llm_model, api_key=config.llm_api_key)

def initialize_agents(llm):
    """Initialize all the agents."""
    filtering_agent = FilteringAgent.create_default(llm)
    extraction_agent = TaskExtractionAgent.create_default(llm)
    formatting_agent = TaskFormattingAgent.create_default(llm)
    return filtering_agent, extraction_agent, formatting_agent

def initialize_tasks(filtering_agent, extraction_agent, formatting_agent):
    """Initialize all tasks."""
    filtering_task = FilteringTask(filtering_agent)
    extraction_task = ExtractionTask(extraction_agent, depends_on=[filtering_task])
    formatting_task = FormattingTask(formatting_agent, depends_on=[extraction_task])
    return filtering_task, extraction_task, formatting_task

def process_messages(messages, agents, tasks):
    """Process messages through the agent workflow."""
    filtering_agent, extraction_agent, formatting_agent = agents
    filtering_task, extraction_task, formatting_task = tasks
    
    crew = Crew(
        agents=[filtering_agent, extraction_agent, formatting_agent],
        tasks=[filtering_task, extraction_task, formatting_task],
        verbose=config.verbose,
        process=config.process_type
    )
    
    result = crew.kickoff(inputs={"messages": messages})
    # Convert CrewOutput to string to ensure it can be parsed as JSON
    return str(result)

def main():
    st.title("TaskFlow Agent")
    st.write("Extract tasks from Slack conversations")
    
    # Sidebar for settings
    st.sidebar.header("Settings")
    channel = st.sidebar.selectbox("Select Channel", ["general", "social", "all-networking-app", "frontend"])
    
    # Initialize components
    llm = initialize_llm()
    agents = initialize_agents(llm)
    tasks = initialize_tasks(*agents)
    
    # Load and display messages
    slack_processor = SlackMessageProcessor()
    messages = slack_processor.load_messages_from_file(channel)
    
    if messages:
        st.write(f"Found {len(messages)} messages in #{channel}")
        
        # Display messages
        with st.expander("View Messages", expanded=False):
            for msg in messages:
                st.write(f"**{msg['username']}**: {msg['message']}")
        
        # Process button
        if st.button("Extract Tasks"):
            with st.spinner("Processing messages..."):
                result = process_messages(messages, agents, tasks)
                
                try:
                    # Display the result in a formatted way
                    tasks = json.loads(result)
                    st.success(f"Found {len(tasks)} tasks!")
                    
                    for i, task in enumerate(tasks):
                        st.markdown(f"### Task {i+1}")
                        st.write(f"**Title:** {task['title']}")
                        st.write(f"**Assignee:** {task['assignee'] or 'Unassigned'}")
                        st.write(f"**Due Date:** {task['dueDate'] or 'No deadline'}")
                        st.divider()
                        
                except json.JSONDecodeError:
                    st.error("Could not parse the extracted tasks. Raw output:")
                    st.code(result)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    else:
        st.warning(f"No messages found in #{channel}. Please select a different channel.")

if __name__ == "__main__":
    main()
