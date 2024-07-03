import unittest
from app import app, db
from test_config import TestConfig
from model import Task

class TaskModelTestCase(unittest.TestCase):
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

    def test_task_creation(self):
        task = Task(
            user_id=1,
            taskname="Test Task",
            fixed=False,
            duration=60,
            preferred_intervals=['09:00-10:00'],
            preferred_days=['Monday'],
            max_intervals=['08:00-18:00'],
            all_days=['Monday', 'Tuesday'],
            difficulty=5,
            importance=7
        )
        db.session.add(task)
        db.session.commit()
        self.assertEqual(task.taskname, 'Test Task')
    
if __name__ == '__main__':
    unittest.main()