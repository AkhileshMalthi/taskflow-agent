import os
import json
import traceback
import streamlit as st
from datetime import datetime

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
from utils.config_manager import ConfigManager

# Load environment variables
load_dotenv()
config = Config.from_env()

# Initialize session state for persistent storage
if 'processed_tasks' not in st.session_state:
    st.session_state.processed_tasks = None
if 'raw_result' not in st.session_state:
    st.session_state.raw_result = None
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'saved_files' not in st.session_state:
    st.session_state.saved_files = []
if 'config_initialized' not in st.session_state:
    st.session_state.config_initialized = False
if 'show_config' not in st.session_state:
    st.session_state.show_config = False

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

def get_saved_files():
    """Get a list of saved files from the data directory."""
    saved_files = []
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        # Ensure data directory exists
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            return saved_files
        
        # List all JSON files in the data directory (including subdirectories)
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    # Get relative path for display (from data dir)
                    rel_path = os.path.relpath(file_path, data_dir)
                    saved_files.append({
                        "name": rel_path,
                        "path": file_path,
                        "date": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M")
                    })
        
        # Sort by modification date (newest first)
        saved_files.sort(key=lambda x: os.path.getmtime(x["path"]), reverse=True)
        return saved_files
    except Exception as e:
        st.error(f"Error loading saved files: {str(e)}")
        return []

def save_uploaded_file(uploaded_file, custom_name=None):
    """Save an uploaded file to the data directory."""
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        # Ensure data directory exists
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Use custom name if provided, otherwise use the original filename
        filename = custom_name if custom_name else uploaded_file.name
        
        # Ensure filename has .json extension
        if not filename.endswith(".json"):
            filename += ".json"
        
        # Save the file
        file_path = os.path.join(data_dir, filename)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return True, file_path
    except Exception as e:
        return False, str(e)

def show_configuration_menu():
    """Show the initial configuration menu to collect API credentials."""
    st.sidebar.header("API Configuration")
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Create tabs for different services
    tab1, tab2, tab3 = st.sidebar.tabs(["LLM", "Trello", "ClickUp"])
    
    with tab1:
        st.subheader("LLM Service")
        groq_api_key = st.text_input("Groq API Key", 
                                     value=config.llm_api_key or "",
                                     type="password",
                                     help="API key for Groq LLM service")
        
        llm_model = st.selectbox("LLM Model", 
                                ["groq/mixtral-8x7b-32768", 
                                 "groq/llama3-70b-8192",
                                 "groq/gemma-7b-it"], 
                                index=0)
    
    with tab2:
        st.subheader("Trello")
        trello_api_key = st.text_input("Trello API Key", 
                                      value=config.trello_api_key or "",
                                      type="password")
        trello_token = st.text_input("Trello Token", 
                                    value=config.trello_api_token or "",
                                    type="password")
        trello_board_id = st.text_input("Trello Board ID (optional)", 
                                       value=config.trello_board_id or "")
        trello_list_id = st.text_input("Trello List ID (optional if Board ID provided)", 
                                      value=config.trello_list_id or "")
    
    with tab3:
        st.subheader("ClickUp")
        clickup_api_token = st.text_input("ClickUp API Token", 
                                         value=config.clickup_api_token or "",
                                         type="password")
        clickup_list_id = st.text_input("ClickUp List ID (optional)", 
                                       value=config.clickup_list_id or "")
        clickup_space_id = st.text_input("ClickUp Space ID (optional if List ID provided)", 
                                        value=config.clickup_space_id or "")
    
    # Save button for configuration
    if st.sidebar.button("Save Configuration"):
        # Create a dictionary with all the configuration values
        new_config = {
            "GROQ_API_KEY": groq_api_key,
            "LLM_MODEL": llm_model,
            "TRELLO_API_KEY": trello_api_key,
            "TRELLO_API_TOKEN": trello_token,
            "TRELLO_BOARD_ID": trello_board_id,
            "TRELLO_LIST_ID": trello_list_id,
            "CLICKUP_API_TOKEN": clickup_api_token,
            "CLICKUP_LIST_ID": clickup_list_id,
            "CLICKUP_SPACE_ID": clickup_space_id
        }
        
        # Save the configuration
        if config_manager.save_config(new_config):
            st.sidebar.success("Configuration saved successfully!")
            # Update the session state
            st.session_state.config_initialized = True
            # Update the config variable
            config.llm_api_key = groq_api_key
            config.llm_model = llm_model
            config.trello_api_key = trello_api_key
            config.trello_api_token = trello_token
            config.trello_board_id = trello_board_id
            config.trello_list_id = trello_list_id
            config.clickup_api_token = clickup_api_token
            config.clickup_list_id = clickup_list_id
            config.clickup_space_id = clickup_space_id
            # Hide the configuration menu
            st.session_state.show_config = False
            # Rerun the app to apply changes
            st.rerun()
        else:
            st.sidebar.error("Failed to save configuration!")
    
    # Cancel button to hide the configuration without saving
    if st.sidebar.button("Cancel"):
        st.session_state.show_config = False
        st.rerun()

def main():
    st.title("TaskFlow Agent")
    st.write("Extract tasks from Slack conversations")
    
    # Show configuration button in the sidebar
    st.sidebar.header("Settings")
    
    # Configuration menu toggle
    if st.sidebar.button("Configuration Menu"):
        st.session_state.show_config = not st.session_state.show_config
        st.rerun()
    
    # Show configuration menu if needed
    if st.session_state.show_config:
        show_configuration_menu()
    
    # First-time setup - show configuration if no API key is set
    config_manager = ConfigManager()
    if not config.llm_api_key and not st.session_state.config_initialized:
        st.info("Welcome to TaskFlow Agent! Please set up your API keys to get started.")
        show_configuration_menu()
        # Only show the configuration menu if no API keys are set
        if not config.llm_api_key:
            return
    
    # Initialize message storage
    messages = []
    
    # File upload section
    st.sidebar.subheader("Upload Conversation File")
    
    # File upload option
    uploaded_file = st.sidebar.file_uploader("Upload Slack export file (JSON)", type=["json"])
    
    if uploaded_file is not None:
        # Option to save the file
        save_file = st.sidebar.checkbox("Save file for future use", value=True)
        
        if save_file:
            custom_name = st.sidebar.text_input("Save as (optional)", 
                                              value=uploaded_file.name,
                                              help="Enter a custom name for this file")
            
            if st.sidebar.button("Save File"):
                success, result = save_uploaded_file(uploaded_file, custom_name)
                if success:
                    st.sidebar.success(f"File saved successfully!")
                    # Update the saved files list
                    st.session_state.saved_files = get_saved_files()
                    # Set as current file
                    st.session_state.current_file = result
                else:
                    st.sidebar.error(f"Failed to save file: {result}")
        
        # Process the uploaded file
        try:
            # Read the file content
            file_content = uploaded_file.getvalue().decode("utf-8")
            # Process the file content
            slack_processor = SlackMessageProcessor()
            messages = slack_processor.parse_messages_from_content(file_content)
            st.write(f"Found {len(messages)} messages in uploaded file")
            # Set as current file
            st.session_state.current_file = "Uploaded file (not saved)"
        except Exception as e:
            st.error(f"Error processing uploaded file: {str(e)}")
    
    # Display saved files
    st.sidebar.subheader("Saved Files")
    
    # Refresh saved files list
    if st.sidebar.button("Refresh"):
        st.session_state.saved_files = get_saved_files()
    
    # Load saved files if not in session state
    if not st.session_state.saved_files:
        st.session_state.saved_files = get_saved_files()
    
    # Display saved files
    if st.session_state.saved_files:
        selected_file = st.sidebar.selectbox(
            "Select saved file", 
            options=[f["name"] for f in st.session_state.saved_files],
            format_func=lambda x: x
        )
        
        # Get the selected file path
        selected_file_path = next((f["path"] for f in st.session_state.saved_files if f["name"] == selected_file), None)
        
        if selected_file_path and st.sidebar.button("Load Selected File"):
            try:
                # Process the selected file
                with open(selected_file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    
                slack_processor = SlackMessageProcessor()
                messages = slack_processor.parse_messages_from_content(file_content)
                st.write(f"Found {len(messages)} messages in {selected_file}")
                # Set as current file
                st.session_state.current_file = selected_file
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
        
        # File management options
        if selected_file_path:
            if st.sidebar.button("Delete Selected File"):
                try:
                    os.remove(selected_file_path)
                    st.sidebar.success(f"File '{selected_file}' deleted successfully")
                    # Update saved files list
                    st.session_state.saved_files = get_saved_files()
                    # Clear current file if it was the deleted one
                    if st.session_state.current_file == selected_file:
                        st.session_state.current_file = None
                        st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Failed to delete file: {str(e)}")
    else:
        st.sidebar.info("No saved files. Upload a file and save it for future use.")
    
    # Show current file if any
    if st.session_state.current_file:
        st.info(f"Currently working with: {st.session_state.current_file}")
    
    # Advanced options
    with st.sidebar.expander("Advanced Options"):
        show_raw_output = st.checkbox("Show Raw Output", value=False)
        use_enhanced_extraction = st.checkbox("Use Enhanced Extraction", value=True)
    
    # Initialize components
    try:
        llm = initialize_llm()
        agents = initialize_agents(llm)
        tasks = initialize_tasks(*agents)
    except Exception as e:
        st.error(f"Initialization failed. Please check your API keys and configuration. Error: {str(e)}")
        # Show the configuration menu if initialization fails
        if not st.session_state.show_config:
            if st.button("Open Configuration Menu"):
                st.session_state.show_config = True
                st.rerun()
        return
    
    if messages:
        # Display messages
        with st.expander("View Messages", expanded=False):
            for msg in messages:
                # Format the username - use real_name from user_profile if available
                if 'user_profile' in msg and msg['user_profile'].get('real_name'):
                    username = msg['user_profile']['real_name']
                else:
                    username = msg.get('username', 'Unknown User')
                
                # Display the message with proper formatting
                st.markdown(f"**{username}**: {msg.get('message', '')}")
                
                # Add a timestamp if available
                if msg.get('timestamp'):
                    try:
                        # Try to format timestamp nicely if it's a float
                        ts = float(msg['timestamp'])
                        from datetime import datetime
                        timestamp = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                        st.caption(f"Time: {timestamp}")
                    except (ValueError, TypeError):
                        # If not a float, use as is
                        st.caption(f"Time: {msg['timestamp']}")
                
                # Add a separator between messages
                st.markdown("---")
        
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
        st.info("Please upload a conversation file or select a saved file to extract tasks.")

if __name__ == "__main__":
    main()
