# tests/test_routes/test_get_tasks.py
import unittest
from app import app, db, Task
from test_config import TestConfig

# Test to ensure that we can getTasks by user id
class GetTasksTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object(TestConfig)
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        task1 = Task(
            user_id=1,
            taskname='Test Task 1',
            fixed=False,
            duration=60,
            preferred_intervals=['09:00-10:00'],
            preferred_days=['Monday'],
            max_intervals=['08:00-18:00'],
            all_days=['Monday', 'Tuesday'],
            difficulty=5,
            importance=7
        )
        task2 = Task(
            user_id=1,
            taskname='Test Task 2',
            fixed=True,
            duration=30,
            preferred_intervals=['10:00-10:30'],
            preferred_days=['Tuesday'],
            max_intervals=['08:00-18:00'],
            all_days=['Tuesday'],
            difficulty=3,
            importance=8
        )
        db.session.add(task1)
        db.session.add(task2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_tasks(self):
        response = self.app.get('/getTasks/1')
        self.assertEqual(response.status_code, 200)
        tasks = response.get_json()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['taskname'], 'Test Task 1')
        self.assertEqual(tasks[1]['taskname'], 'Test Task 2')

if __name__ == '__main__':
    unittest.main()
