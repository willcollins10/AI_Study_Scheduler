# tests/test_routes/test_add_task.py
import unittest
from app import app, db
from model import Task
from test_config import TestConfig

# TODO: test for when you try to add a task with invalid data (i.e a string for duration)
class AddTaskTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object(TestConfig)
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_task(self):
        # Create a dictionary with what expect attributes to equal
        expected_task_data = {
            'user_id': 1,
            'taskname': 'Test Task',
            'fixed': False,
            'duration': 60,
            'preferred_intervals': ['09:00-10:00'],
            'preferred_days': ['Monday'],
            'max_intervals': ['08:00-18:00'],
            'all_days': ['Monday', 'Tuesday'],
            'difficulty': 5,
            'importance': 7
        }
         # Add task via POST request & check that it was successful added
        response = self.app.post('/addTask', json=expected_task_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Task added successfully', response.get_data(as_text=True))

         # Fetch the task from the database
        task = Task.query.filter_by(user_id=expected_task_data['user_id'], taskname=expected_task_data['taskname']).first()
        self.assertIsNotNone(task, "Task should exist in the database")

        # Check each attribute and make sure it is the same as expected_task_data
        self.assertEqual(task.user_id, expected_task_data['user_id'])
        self.assertEqual(task.taskname, expected_task_data['taskname'])
        self.assertEqual(task.fixed, expected_task_data['fixed'])
        self.assertEqual(task.duration, expected_task_data['duration'])
        self.assertEqual(task.preferred_intervals, expected_task_data['preferred_intervals'])
        self.assertEqual(task.preferred_days, expected_task_data['preferred_days'])
        self.assertEqual(task.max_intervals, expected_task_data['max_intervals'])
        self.assertEqual(task.all_days, expected_task_data['all_days'])
        self.assertEqual(task.difficulty, expected_task_data['difficulty'])
        self.assertEqual(task.importance, expected_task_data['importance'])



if __name__ == '__main__':
    unittest.main()
