import unittest
from app import app, db
from model import Task
from test_config import TestConfig

class DeleteTaskTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object(TestConfig)
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Add a sample task to the database
        self.task = Task(
            user_id=1,
            taskname='Task to be deleted',
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

    def test_delete_task_success(self):
        response = self.app.delete(f'/deleteTask/{self.task.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Task deleted successfully', response.get_data(as_text=True))

        # Verify that the task is no longer in the database
        deleted_task = Task.query.get(self.task.id)
        self.assertIsNone(deleted_task)

    # Deleting a task that doesn't exist
    def test_delete_task_not_found(self):
        response = self.app.delete('/deleteTask/9999')  # Assuming 9999 is a non-existent task ID
        self.assertEqual(response.status_code, 404)
        self.assertIn('Task not found', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
