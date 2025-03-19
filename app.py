import os
import json
import traceback
import streamlit as st

# Configure environment to avoid dependency issues
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# Disable ChromaDB in CrewAI
os.environ["CREWAI_MEMORY_ENABLE"] = "false"

# Now import crewai components
from crewai import Crew
from langchain_groq import ChatGroq
from dotenv import load_dotenv

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

# Initialize session state for persistent storage
if 'processed_tasks' not in st.session_state:
    st.session_state.processed_tasks = None
if 'raw_result' not in st.session_state:
    st.session_state.raw_result = None

def initialize_llm():
    """Initialize the language model."""
    try:
        return ChatGroq(model=config.llm_model, api_key=config.llm_api_key)
    except Exception as e:
        st.error(f"Error initializing LLM: {str(e)}")
        raise

def initialize_agents(llm):
    """Initialize all the agents."""
    try:
        filtering_agent = FilteringAgent.create_default(llm)
        extraction_agent = TaskExtractionAgent.create_default(llm)
        formatting_agent = TaskFormattingAgent.create_default(llm)
        return filtering_agent, extraction_agent, formatting_agent
    except Exception as e:
        st.error(f"Error initializing agents: {str(e)}")
        raise

def initialize_tasks(filtering_agent, extraction_agent, formatting_agent):
    """Initialize all tasks."""
    try:
        filtering_task = FilteringTask(filtering_agent)
        extraction_task = ExtractionTask(extraction_agent, depends_on=[filtering_task])
        formatting_task = FormattingTask(formatting_agent, depends_on=[extraction_task])
        return filtering_task, extraction_task, formatting_task
    except Exception as e:
        st.error(f"Error initializing tasks: {str(e)}")
        raise

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
    
    try:
        result = crew.kickoff(inputs={"messages": messages})
        # Convert CrewOutput to string to ensure it can be parsed as JSON
        return str(result)
    except Exception as e:
        # Get detailed stack trace
        stack_trace = traceback.format_exc()
        st.error(f"API Error: {str(e)}\n\n{stack_trace}")
        return None

def display_tasks(tasks):
    """Display extracted tasks in the UI."""
    st.success(f"Found {len(tasks)} tasks!")
    
    # Display tasks in a more visual format
    for i, task in enumerate(tasks):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {task['title']}")
                if task.get('description'):
                    st.write(task['description'])
            
            with col2:
                priority = task.get('priority', 'Medium')
                priority_color = {
                    'High': 'red',
                    'Medium': 'orange',
                    'Low': 'green'
                }.get(priority, 'gray')
                
                st.markdown(f"<span style='color:{priority_color};font-weight:bold;'>{priority}</span>", 
                            unsafe_allow_html=True)
            
            st.write(f"**Assignee:** {task.get('assignee', 'Unassigned')}")
            st.write(f"**Due Date:** {task.get('dueDate', 'No deadline')}")
            
            if task.get('status'):
                st.write(f"**Status:** {task['status']}")
                
            st.divider()

def handle_export(tasks):
    """Handle task export workflow."""
    st.subheader("Export Tasks")
    
    # Export option selection
    export_option = st.selectbox("Export to:", ["JSON File", "Trello", "ClickUp"], key="export_option")
    
    # Show configuration inputs based on selected export option
    export_config = {}
    
    if export_option == "Trello":
        with st.expander("Trello Configuration", expanded=not config.trello_api_key):
            export_config["api_key"] = st.text_input("Trello API Key", 
                                      value=config.trello_api_key or "", 
                                      type="password", key="trello_api_key")
            export_config["token"] = st.text_input("Trello Token", 
                                    value=config.trello_api_token or "", 
                                    type="password", key="trello_token")
            export_config["board_id"] = st.text_input("Trello Board ID", 
                                      value=config.trello_board_id or "", key="trello_board_id")
            export_config["list_id"] = st.text_input("Trello List ID (optional if Board ID provided)", 
                                     value=config.trello_list_id or "", key="trello_list_id")
    elif export_option == "ClickUp":
        with st.expander("ClickUp Configuration", expanded=not config.clickup_api_token):
            export_config["api_token"] = st.text_input("ClickUp API Token", 
                                        value=config.clickup_api_token or "", 
                                        type="password", key="clickup_api_token")
            export_config["list_id"] = st.text_input("ClickUp List ID", 
                                      value=config.clickup_list_id or "", key="clickup_list_id")
            export_config["space_id"] = st.text_input("ClickUp Space ID (optional if List ID provided)", 
                                       value=config.clickup_space_id or "", key="clickup_space_id")
    
    if st.button("Export Tasks", key="export_button"):
        try:
            if export_option == "JSON File":
                from integrations.task_exporter import FileExporter
                exporter = FileExporter()
            elif export_option == "Trello":
                from integrations.task_exporter import TrelloExporter
                exporter = TrelloExporter(**export_config)
            else:  # ClickUp
                from integrations.task_exporter import ClickUpExporter
                exporter = ClickUpExporter(**export_config)
                
            with st.spinner(f"Exporting tasks to {export_option}..."):
                success = exporter.export_tasks(tasks)
                if success:
                    st.success(f"Successfully exported tasks to {export_option}")
                else:
                    st.error(f"Failed to export tasks to {export_option}")
        except Exception as e:
            st.error(f"Export error: {str(e)}")

def get_available_channels():
    """Get a list of available channels from the data directory."""
    try:
        data_dir = "d:\\Projects\\taskflow-agent\\data"
        # List all directories in the data folder, which represent channels
        channels = [f for f in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, f))]
        return channels if channels else ["general"]  # Return at least "general" if no channels found
    except Exception as e:
        st.sidebar.warning(f"Error loading channels: {str(e)}")
        return ["general"]  # Fallback to general

def main():
    st.title("TaskFlow Agent")
    st.write("Extract tasks from Slack conversations")
    
    # Sidebar for settings
    st.sidebar.header("Settings")
    
    # Add data source selection
    data_source = st.sidebar.radio("Data Source", ["Predefined Channels", "Upload File"])
    
    # Initialize message storage
    messages = []
    
    if data_source == "Predefined Channels":
        # Dynamically load available channels from data directory
        available_channels = get_available_channels()
        channel = st.sidebar.selectbox("Select Channel", available_channels)
        
        # Load messages from selected channel
        try:
            slack_processor = SlackMessageProcessor()
            messages = slack_processor.load_messages_from_file(channel)
            st.write(f"Found {len(messages)} messages in #{channel}")
        except Exception as e:
            st.error(f"Error loading messages: {str(e)}")
    else:
        # File upload option
        uploaded_file = st.sidebar.file_uploader("Upload Slack export file (JSON)", type=["json"])
        
        if uploaded_file is not None:
            try:
                # Read the file content
                file_content = uploaded_file.getvalue().decode("utf-8")
                # Process the file content
                slack_processor = SlackMessageProcessor()
                messages = slack_processor.parse_messages_from_content(file_content)
                st.write(f"Found {len(messages)} messages in uploaded file")
            except Exception as e:
                st.error(f"Error processing uploaded file: {str(e)}")
    
    # Advanced options
    with st.sidebar.expander("Advanced Options"):
        show_raw_output = st.checkbox("Show Raw Output", value=False)
        use_enhanced_extraction = st.checkbox("Use Enhanced Extraction", value=True)
    
    # Initialize components
    try:
        llm = initialize_llm()
        agents = initialize_agents(llm)
        tasks = initialize_tasks(*agents)
    except Exception:
        st.error("Initialization failed. Please check your API keys and configuration.")
        return
    
    if messages:
        # Display messages
        with st.expander("View Messages", expanded=False):
            for msg in messages:
                st.write(f"**{msg['username']}**: {msg['message']}")
        
        # Check if we need to process messages or use cached results
        col1, col2 = st.columns([1, 1])
        
        extract_clicked = col1.button("Extract Tasks")
        clear_clicked = col2.button("Clear Results")
        
        if clear_clicked:
            st.session_state.processed_tasks = None
            st.session_state.raw_result = None
            st.rerun()
        
        if extract_clicked:
            with st.spinner("Processing messages..."):
                result = process_messages(messages, agents, tasks)
                
                if not result:
                    # Error was already displayed in process_messages
                    return
                
                try:
                    # Parse the JSON result
                    parsed_tasks = json.loads(result)
                    
                    # Store in session state
                    st.session_state.processed_tasks = parsed_tasks
                    st.session_state.raw_result = result
                    
                except json.JSONDecodeError:
                    st.error("Could not parse the extracted tasks. Raw output:")
                    st.code(result)
                    return
                except Exception as e:
                    st.error(f"Error processing tasks: {str(e)}")
                    return
        
        # Display tasks if we have them (either freshly processed or from session state)
        if st.session_state.processed_tasks:
            # Show raw output if requested
            if show_raw_output and st.session_state.raw_result:
                with st.expander("Raw JSON Output"):
                    st.code(st.session_state.raw_result, language="json")
            
            # Display the tasks
            display_tasks(st.session_state.processed_tasks)
            
            # Handle export functionality
            handle_export(st.session_state.processed_tasks)
    else:
        if data_source == "Predefined Channels":
            st.warning(f"No messages found in the selected channel. Please select a different channel.")
        else:
            st.info("Please upload a Slack export file to extract tasks.")

if __name__ == "__main__":
    main()
