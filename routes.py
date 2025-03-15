from flask import render_template, request, jsonify, make_response, Blueprint
from extensions import db
from models import Task, Session, Conversation
from datetime import datetime
import logging
import hmac
import hashlib
import os

logger = logging.getLogger(__name__)

# Define blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)
slack_bp = Blueprint('slack', __name__)

# Try/except to handle the potential import error of slack_bot
try:
    from slack_bot import slack_bot
except ImportError:
    # Create a simple mock if slack_bot is not available
    class SlackBotMock:
        def handle_interaction(self, payload):
            pass
        def handle_command(self, command, user_id, channel_id):
            pass
    slack_bot = SlackBotMock()

# Main routes
@main_bp.route('/')
def index():
    return render_template('index.html')

# API routes
@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = Task.query.all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            assigned_to=data['assigned_to'],
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        data = request.json
        
        # Update task fields
        for key, value in data.items():
            if key in ['title', 'description', 'assigned_to', 'status', 'priority']:
                setattr(task, key, value)
            elif key == 'due_date' and value:
                task.due_date = datetime.fromisoformat(value)
        
        # Update completed_at if status is changed to completed
        if data.get('status') == 'completed' and task.status != 'completed':
            task.completed_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(task.to_dict())
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sessions', methods=['GET'])
def get_sessions():
    try:
        sessions = Session.query.all()
        return jsonify([s.to_dict() for s in sessions])
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sessions/<int:session_id>/conversations', methods=['GET'])
def get_session_conversations(session_id):
    try:
        conversations = Conversation.query.filter_by(session_id=session_id).all()
        return jsonify([c.to_dict() for c in conversations])
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        return jsonify({'error': str(e)}), 500

# Slack routes
@slack_bp.route('/events', methods=['POST'])
def slack_events():
    try:
        data = request.json
        
        # Verify the request is coming from Slack
        if not verify_slack_request(request):
            return jsonify({'error': 'Invalid signature'}), 401
            
        # Handle URL verification challenge
        if 'challenge' in data:
            return jsonify({'challenge': data['challenge']})
            
        # Process the event
        if 'event' in data:
            event = data['event']
            event_type = event.get('type')
            
            if event_type == 'message':
                # Process message event
                process_message_event(event)
                
            # Add other event types as needed
            
        return jsonify({'status': 'ok'}), 200
        
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        return jsonify({'error': 'Invalid input'}), 400
    except KeyError as e:
        logger.error(f"KeyError: {e}")
        return jsonify({'error': 'Missing key'}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@slack_bp.route('/interactions', methods=['POST'])
def slack_interactions():
    try:
        # Verify Slack signature
        if not request.headers.get('X-Slack-No-Retry') and not verify_slack_request(request):
            return jsonify({'error': 'Invalid signature'}), 401

        # Parse payload
        payload = request.form.get('payload', '{}')
        if isinstance(payload, str):
            import json
            payload = json.loads(payload)

        # Handle interaction
        slack_bot.handle_interaction(payload)
        return jsonify({'status': 'ok'})

    except Exception as e:
        logger.error(f"Error handling Slack interaction: {e}")
        return jsonify({'error': str(e)}), 500

@slack_bp.route('/commands', methods=['POST'])
def slack_commands():
    """Handle Slack slash commands."""
    try:
        # Verify Slack signature
        if not verify_slack_request(request):
            return jsonify({'error': 'Invalid signature'}), 401

        command = request.form.get('command', '')
        user_id = request.form.get('user_id', '')
        channel_id = request.form.get('channel_id', '')

        # Handle the command
        slack_bot.handle_command(command, user_id, channel_id)

        return jsonify({'response_type': 'in_channel'})

    except Exception as e:
        logger.error(f"Error handling Slack command: {e}")
        return jsonify({'error': str(e)}), 500

def verify_slack_request(request):
    """Verify that the request comes from Slack."""
    # In debug/development, skip verification
    if os.environ.get('FLASK_ENV') == 'development':
        return True
        
    slack_signing_secret = os.environ.get('SLACK_SIGNING_SECRET')
    if not slack_signing_secret:
        logger.warning("SLACK_SIGNING_SECRET not configured")
        return False
        
    timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    signature = request.headers.get('X-Slack-Signature', '')
    
    # Create the signature base string
    request_body = request.get_data().decode('utf-8')
    sig_basestring = f"v0:{timestamp}:{request_body}"
    
    # Calculate the signature
    my_signature = 'v0=' + hmac.new(
        slack_signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(my_signature, signature)

def process_message_event(event):
    """Process a message event from Slack."""
    # Implementation of message processing logic
    pass