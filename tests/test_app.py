import unittest
import json
import os
from datetime import datetime, timedelta
from app import app, db
from models import Session, Conversation, Task

class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test data
        self._create_test_data()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def _create_test_data(self):
        # Create test session
        session = Session(
            channel_id='C123456',
            started_by='U123456',
            status='active'
        )
        db.session.add(session)
        db.session.commit()
        
        # Create test conversation
        conversation = Conversation(
            session_id=session.id,
            user_id='U123456',
            message='Let\'s discuss the project timeline'
        )
        db.session.add(conversation)
        
        # Create test task
        task = Task(
            title='Complete unit tests',
            description='Create comprehensive test suite',
            assigned_to='U123456',
            session_id=session.id,
            due_date=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(task)
        db.session.commit()
    
    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_slack_events(self):
        response = self.app.post('/slack/events', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_get_tasks(self):
        response = self.app.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Complete unit tests')
    
    def test_create_task(self):
        task_data = {
            'title': 'New test task',
            'description': 'Test task creation',
            'assigned_to': 'U789012',
            'due_date': '2023-12-31T23:59:59'
        }
        response = self.app.post(
            '/api/tasks',
            data=json.dumps(task_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Verify task was created
        tasks = Task.query.filter_by(title='New test task').all()
        self.assertEqual(len(tasks), 1)
    
    def test_update_task(self):
        task = Task.query.first()
        task_id = task.id
        
        update_data = {
            'status': 'completed'
        }
        response = self.app.put(
            f'/api/tasks/{task_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify task was updated
        updated_task = Task.query.get(task_id)
        self.assertEqual(updated_task.status, 'completed')
    
    def test_delete_task(self):
        task = Task.query.first()
        task_id = task.id
        
        response = self.app.delete(f'/api/tasks/{task_id}')
        self.assertEqual(response.status_code, 204)
        
        # Verify task was deleted
        deleted_task = Task.query.get(task_id)
        self.assertIsNone(deleted_task)

if __name__ == '__main__':
    unittest.main()
