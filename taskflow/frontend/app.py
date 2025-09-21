"""
Streamlit Frontend for Taskflow Agent MVP.
Provides a simple UI for message submission and task viewing.
"""

import streamlit as st
import time
from datetime import datetime
from typing import List, Dict

from taskflow.backend.ingestor.service import create_ingestor_service
from taskflow.backend.platform_manager.service import PlatformManager


def init_session_state():
    """Initialize Streamlit session state."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
    if 'ingestor_service' not in st.session_state:
        try:
            st.session_state.ingestor_service = create_ingestor_service()
            st.session_state.service_connected = True
        except Exception as e:
            st.session_state.service_connected = False
            st.session_state.connection_error = str(e)
    if 'platform_manager' not in st.session_state:
        st.session_state.platform_manager = PlatformManager()


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Taskflow Agent MVP",
        page_icon="🤖",
        layout="wide"
    )
    
    init_session_state()
    
    # Header
    st.title("🤖 Taskflow Agent MVP")
    st.markdown("Event-driven task extraction from conversations using RabbitMQ")
    
    # Check service connection
    if not st.session_state.get('service_connected', False):
        st.error(f"❌ Failed to connect to services: {st.session_state.get('connection_error', 'Unknown error')}")
        st.info("💡 Make sure RabbitMQ is running and accessible.")
        st.stop()
    
    st.success("✅ Connected to Taskflow services")
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Controls")
        
        # Service status
        st.subheader("Service Status")
        st.write("🟢 Ingestor Service: Connected")
        st.write("🟢 Message Broker: Connected")
        
        # Clear data
        if st.button("🗑️ Clear All Data"):
            st.session_state.messages = []
            st.session_state.tasks = []
            st.rerun()
        
        # Instructions
        st.subheader("📋 Instructions")
        st.markdown("""
        1. **Submit Messages**: Enter conversation messages in the form below
        2. **View Tasks**: See extracted tasks in real-time
        3. **Task Extraction**: The AI looks for actionable items in your messages
        
        **Tip**: Try messages like:
        - "We need to fix the login bug by Friday"
        - "Can someone please review the new design?"
        - "@john please update the documentation ASAP"
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Submit Message")
        
        # Message submission form
        with st.form("message_form"):
            content = st.text_area(
                "Message Content",
                placeholder="Enter your conversation message here...",
                height=100
            )
            
            col_author, col_channel = st.columns(2)
            with col_author:
                author = st.text_input("Author", value="demo_user")
            with col_channel:
                channel = st.text_input("Channel (optional)", placeholder="#general")
            
            source = st.selectbox("Source", ["manual", "slack", "teams", "email"])
            
            submitted = st.form_submit_button("🚀 Submit Message")
        
        if submitted and content.strip():
            try:
                # Ingest the message
                message_id = st.session_state.ingestor_service.ingest_message(
                    content=content,
                    author=author,
                    source=source,
                    channel=channel if channel else None
                )
                
                # Store in session state
                st.session_state.messages.append({
                    "id": message_id,
                    "content": content,
                    "author": author,
                    "source": source,
                    "channel": channel,
                    "timestamp": datetime.now()
                })
                
                st.success(f"✅ Message submitted! ID: {message_id[:8]}...")
                
                # Simulate task extraction (in real implementation, this would be async)
                st.info("🤖 AI is processing your message for task extraction...")
                time.sleep(1)  # Simulate processing time
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error submitting message: {e}")
        elif submitted:
            st.warning("⚠️ Please enter a message content")
    
    with col2:
        st.header("📋 Recent Messages")
        
        # Display recent messages
        if st.session_state.messages:
            for msg in reversed(st.session_state.messages[-5:]):  # Show last 5 messages
                with st.expander(f"💬 {msg['author']} - {msg['timestamp'].strftime('%H:%M:%S')}"):
                    st.write(f"**Content:** {msg['content']}")
                    st.write(f"**Source:** {msg['source']}")
                    if msg['channel']:
                        st.write(f"**Channel:** {msg['channel']}")
                    st.write(f"**ID:** {msg['id']}")
        else:
            st.info("No messages submitted yet. Use the form on the left to submit your first message!")
    
    # Tasks section
    st.header("🎯 Extracted Tasks")
    
    # Get tasks from platform manager
    all_tasks = st.session_state.platform_manager.get_all_tasks()
    
    if any(tasks for tasks in all_tasks.values()):
        # Task summary
        total_tasks = sum(len(tasks) for tasks in all_tasks.values())
        st.metric("Total Tasks", total_tasks)
        
        # Display tasks by platform
        for platform_name, tasks in all_tasks.items():
            if tasks:
                st.subheader(f"📝 {platform_name.title()} Tasks")
                
                for task in tasks:
                    with st.expander(f"🎯 {task['title']} - {task['priority'].upper()} priority"):
                        col_task1, col_task2 = st.columns(2)
                        
                        with col_task1:
                            st.write(f"**Description:** {task['description']}")
                            st.write(f"**Priority:** {task['priority']}")
                            st.write(f"**Status:** {task['status']}")
                        
                        with col_task2:
                            st.write(f"**Task ID:** {task['platform_task_id']}")
                            st.write(f"**Created:** {task['created_at'][:19]}")
                            if task['assigned_to']:
                                st.write(f"**Assigned to:** {task['assigned_to']}")
                            if task['due_date']:
                                st.write(f"**Due Date:** {task['due_date'][:19]}")
                        
                        if task['labels']:
                            st.write(f"**Labels:** {', '.join(task['labels'])}")
    else:
        st.info("🤖 No tasks extracted yet. Submit messages above to see AI-generated tasks appear here!")
    
    # Footer
    st.markdown("---")
    st.markdown("🚀 **Taskflow Agent MVP** - Event-driven task extraction powered by RabbitMQ")


if __name__ == "__main__":
    main()