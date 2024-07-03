import unittest
from app import app, db
from model import Task
from test_config import TestConfig
from datetime import datetime

# Test of adding a task with 5 preferred intervals and changing 1 of the intervals
class TaskComplexUpdate(unittest.TestCase):
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

    def test_add_and_update_non_fixed_task(self):
        # Step 1: Add a non-fixed task with 5 preferred intervals
        non_fixed_task_data = {
            'user_id': 1,
            'taskname': 'Non Fixed Task',
            'fixed': False,
            'duration': 120,
            'preferred_intervals': [
                '09:00-10:00',
                '10:00-11:00',
                '11:00-12:00',
                '12:00-13:00',
                '13:00-14:00'
            ],
            'preferred_days': ['Monday', 'Wednesday', 'Friday'],
            'max_intervals': ['08:00-18:00'],
            'all_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'difficulty': 5,
            'importance': 7
        }

        response = self.app.post('/addTask', json=non_fixed_task_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Task added successfully', response.get_data(as_text=True))

        task = Task.query.filter_by(taskname='Non Fixed Task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.fixed, False)
        self.assertEqual(task.duration, 120)
        self.assertEqual(task.preferred_intervals, [
            '09:00-10:00',
            '10:00-11:00',
            '11:00-12:00',
            '12:00-13:00',
            '13:00-14:00'
        ])
        self.assertEqual(task.preferred_days, ['Monday', 'Wednesday', 'Friday'])
        self.assertEqual(task.max_intervals, ['08:00-18:00'])
        self.assertEqual(task.all_days, ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        self.assertEqual(task.difficulty, 5)
        self.assertEqual(task.importance, 7)

        # Step 2: Update the task by changing one preferred interval
        update_data = {
            'preferred_intervals': [
                '09:00-10:00',
                '10:00-11:00',
                '11:00-12:00',
                '12:00-13:00',
                '14:00-15:00'  # Changed interval
            ]
        }

        response = self.app.put(f'/updateTask/{task.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Task updated successfully', response.get_data(as_text=True))

        updated_task = Task.query.get(task.id)
        self.assertEqual(updated_task.preferred_intervals, [
            '09:00-10:00',
            '10:00-11:00',
            '11:00-12:00',
            '12:00-13:00',
            '14:00-15:00'  # Ensure this is updated correctly
        ])
        self.assertEqual(updated_task.taskname, 'Non Fixed Task')  # Unchanged fields
        self.assertEqual(updated_task.fixed, False)
        self.assertEqual(updated_task.duration, 120)
        self.assertEqual(updated_task.preferred_days, ['Monday', 'Wednesday', 'Friday'])
        self.assertEqual(updated_task.max_intervals, ['08:00-18:00'])
        self.assertEqual(updated_task.all_days, ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        self.assertEqual(updated_task.difficulty, 5)
        self.assertEqual(updated_task.importance, 7)

if __name__ == '__main__':
    unittest.main()
