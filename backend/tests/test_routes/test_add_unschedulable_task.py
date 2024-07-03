import unittest
from app import app, db
from model import Task, UnschedulableTask
from datetime import datetime
from test_config import TestConfig

class AddUnschedulableTaskTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object(TestConfig)
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Add a sample task to the database
        self.task = Task(
            user_id=1,
            taskname='Sample Task',
            fixed=False,
            duration=60,
            preferred_intervals=['09:00-10:00'],
            preferred_days=['Monday'],
            max_intervals=['08:00-18:00'],
            all_days=['Monday', 'Tuesday'],
            difficulty=5,
            importance=7
        )
        db.session.add(self.task)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_unschedulable_task_success(self):
        response = self.app.post('/addUnschedulableTask', json={'task_id': self.task.id})
        self.assertEqual(response.status_code, 201)
        self.assertIn('Unschedulable task added successfully', response.get_data(as_text=True))

        unschedulable_task = UnschedulableTask.query.filter_by(task_id=self.task.id).first()
        self.assertIsNotNone(unschedulable_task)

    def test_add_unschedulable_task_invalid_task_id(self):
        response = self.app.post('/addUnschedulableTask', json={'task_id': 'invalid'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid data: task_id must be provided and must be an integer', response.get_data(as_text=True))

    def test_add_unschedulable_task_nonexistent_task(self):
        response = self.app.post('/addUnschedulableTask', json={'task_id': 9999})
        self.assertEqual(response.status_code, 404)
        self.assertIn('Task not found', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
