import os
import logging
from typing import Optional, Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from extensions import db
from converstation_handler import ConversationHandler
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SlackBot:
    def __init__(self):
        self.token = os.environ.get('SLACK_BOT_TOKEN')
        self.channel_id = os.environ.get('SLACK_CHANNEL_ID', '')
        if not self.token:
            logger.warning("SLACK_BOT_TOKEN not set")
            self.client = None
        else:
            self.client = WebClient(token=self.token)
        self.conversation_handler = ConversationHandler()

    def start_session(self, channel_id: str, user_id: str) -> None:
        """Start a new task monitoring session."""
        try:
            if not self.client:
                logger.warning("Slack client not initialized")
                return None
                
            # Import here to avoid circular imports
            from models import Session
            
            # Create new session
            session = Session(
                channel_id=channel_id,
                started_by=user_id,
                status='active'
            )
            db.session.add(session)
            db.session.commit()

            # Send session start message with End Session button
            self.client.chat_postMessage(
                channel=channel_id,
                text=f"Task monitoring session started by <@{user_id}>",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Task monitoring session started by <@{user_id}>"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "End Session"
                                },
                                "style": "danger",
                                "value": f"end_session_{session.id}"
                            }
                        ]
                    }
                ]
            )
            return session.id

        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return None

    def end_session(self, session_id: int) -> None:
        """End a task monitoring session."""
        try:
            # Import here to avoid circular imports
            from models import Session
            
            session = Session.query.get(session_id)
            if session and self.client:
                session.end_time = datetime.utcnow()
                session.status = 'ended'
                db.session.commit()

                self.client.chat_postMessage(
                    channel=session.channel_id,
                    text="Task monitoring session ended"
                )

        except Exception as e:
            logger.error(f"Error ending session: {e}")

    def handle_message(self, event_data: Dict[str, Any]) -> None:
        """Handle incoming Slack messages."""
        try:
            if 'text' not in event_data or 'user' not in event_data:
                return

            # Import here to avoid circular imports
            from models import Session, Conversation, Task
                
            channel_id = event_data.get('channel')
            user_id = event_data['user']
            text = event_data['text']

            # Find active session for this channel
            active_session = Session.query.filter_by(
                channel_id=channel_id,
                status='active'
            ).first()

            if active_session:
                # Store conversation
                conversation = Conversation(
                    session_id=active_session.id,
                    user_id=user_id,
                    message=text
                )
                db.session.add(conversation)
                db.session.commit()

                # Process message for potential tasks
                potential_tasks = self.conversation_handler.extract_potential_tasks(
                    [{"user": user_id, "text": text}]
                )

                if potential_tasks:
                    for task in potential_tasks:
                        self._send_task_approval_request(task, active_session.id)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def handle_interaction(self, payload: Dict[str, Any]) -> None:
        """Handle interactive component interactions."""
        try:
            if not self.client:
                logger.warning("Slack client not initialized")
                return
                
            action_id = payload.get('actions', [{}])[0].get('value', '')

            if action_id.startswith('end_session_'):
                session_id = int(action_id.split('_')[-1])
                self.end_session(session_id)

            elif action_id.startswith('approve_task_'):
                task_id = int(action_id.split('_')[-1])
                self._handle_task_approval(task_id, 'approved', payload.get('user', {}).get('id'))

            elif action_id.startswith('reject_task_'):
                task_id = int(action_id.split('_')[-1])
                self._handle_task_approval(task_id, 'rejected', payload.get('user', {}).get('id'))

        except Exception as e:
            logger.error(f"Error handling interaction: {e}")

    def _send_task_approval_request(self, task_data: Dict, session_id: int) -> None:
        """Send a task approval request to Slack."""
        try:
            if not self.client or not self.channel_id:
                logger.warning("Slack client not initialized or channel not set")
                return
                
            # Import here to avoid circular imports
            from models import Task
                
            # Create pending task
            task = Task(
                title=task_data['title'],
                description=task_data.get('description', ''),
                assigned_to=task_data['assigned_to'],
                session_id=session_id,
                approval_status='pending',
                due_date=datetime.fromisoformat(task_data['due_date']) if task_data.get('due_date') else None
            )
            db.session.add(task)
            db.session.commit()

            # Send approval request with more context
            priority_emoji = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(task_data.get('priority', 'medium'), '⚪')

            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*New Task Detected* {priority_emoji}\n"
                               f"*Title:* {task.title}\n"
                               f"*Assigned to:* <@{task.assigned_to}>\n"
                               f"*Description:* {task.description}\n"
                               f"*Due Date:* {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Not set'}\n"
                               f"*Priority:* {task_data.get('priority', 'medium').title()}"
                    }
                }
            ]

            # Add context if available
            if task_data.get('context'):
                context_text = "\n".join([
                    f"• <@{msg['user']}>: {msg['text']}"
                    for msg in task_data['context']
                ])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Conversation Context:*\n{context_text}"
                    }
                })

            # Add approval buttons
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Approve"
                        },
                        "style": "primary",
                        "value": f"approve_task_{task.id}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Reject"
                        },
                        "style": "danger",
                        "value": f"reject_task_{task.id}"
                    }
                ]
            })

            self.client.chat_postMessage(
                channel=self.channel_id,
                text=f"New task identified: {task.title}",
                blocks=blocks
            )

        except Exception as e:
            logger.error(f"Error sending task approval request: {e}")

    def _handle_task_approval(self, task_id: int, status: str, approver_id: str) -> None:
        """Handle task approval/rejection."""
        try:
            if not self.client or not self.channel_id:
                logger.warning("Slack client not initialized or channel not set")
                return
                
            # Import here to avoid circular imports
            from models import Task
                
            task = Task.query.get(task_id)
            if task:
                task.approval_status = status
                db.session.commit()

                if status == 'approved':
                    # Here we'll add integration with Trello/Clickup
                    self.client.chat_postMessage(
                        channel=self.channel_id,
                        text=f"Task approved and created: {task.title}\n"
                             f"Assigned to: <@{task.assigned_to}>"
                    )
                else:
                    self.client.chat_postMessage(
                        channel=self.channel_id,
                        text=f"Task rejected: {task.title}"
                    )

        except Exception as e:
            logger.error(f"Error handling task approval: {e}")

    def handle_command(self, command, user_id, channel_id):
        """Handle slash commands from Slack."""
        try:
            if not self.client:
                logger.warning("Slack client not initialized - missing token")
                return

            if command == '/taskflow':
                # Handle taskflow command
                self.client.chat_postMessage(
                    channel=channel_id,
                    text=f"Hello <@{user_id}>! TaskFlow is ready to help you track tasks."
                )
            
        except SlackApiError as e:
            logger.error(f"Error sending Slack message: {e}")
        except Exception as e:
            logger.error(f"Error handling Slack command: {e}")

# Initialize singleton instance
slack_bot = SlackBot()