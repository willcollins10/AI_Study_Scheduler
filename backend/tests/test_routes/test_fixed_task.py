import unittest
from app import app, db
from model import Task
from test_config import TestConfig
from datetime import datetime

class TaskFixedCase(unittest.TestCase):
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

    # Test case for adding a fixed task
    def test_add_fixed_task(self):
        fixed_task_data = {
            'user_id': 1,
            'taskname': 'Fixed Task',
            'fixed': True,
            'duration': 60,
            'fixed_day': 'Monday',
            'fixed_start_time': '10:00',
            'fixed_end_time': '11:00'
        }
        response = self.app.post('/addTask', json=fixed_task_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Task added successfully', response.get_data(as_text=True))

        task = Task.query.filter_by(taskname='Fixed Task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.fixed, True)
        self.assertEqual(task.duration, 60)
        self.assertEqual(task.fixed_day, 'Monday')
        self.assertEqual(task.fixed_start_time, datetime.strptime('10:00', '%H:%M').time())
        self.assertEqual(task.fixed_end_time, datetime.strptime('11:00', '%H:%M').time())

    # Test case for updating a task from fixed to not fixed
    def test_update_fixed_to_not_fixed(self):
        fixed_task = Task(
            user_id=1,
            taskname='Fixed Task',
            duration=60,
            fixed=True,
            fixed_day='Monday',
            fixed_start_time=datetime.strptime('10:00', '%H:%M').time(),
            fixed_end_time=datetime.strptime('11:00', '%H:%M').time()
        )
        db.session.add(fixed_task)
        db.session.commit()

        update_data = {
            'taskname': 'Not Fixed Task',
            'fixed': False,
            'duration': 90,
            'preferred_intervals': ['10:00-11:00'],
            'preferred_days': ['Tuesday'],
            'max_intervals': ['09:00-17:00'],
            'all_days': ['Tuesday', 'Wednesday'],
            'difficulty': 8,
            'importance': 9
        }
        response = self.app.put(f'/updateTask/{fixed_task.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Task updated successfully', response.get_data(as_text=True))

        updated_task = Task.query.get(fixed_task.id)
        self.assertEqual(updated_task.taskname, 'Not Fixed Task')
        self.assertEqual(updated_task.fixed, False)
        self.assertEqual(updated_task.duration, 90)
        self.assertEqual(updated_task.preferred_intervals, ['10:00-11:00'])
        self.assertEqual(updated_task.preferred_days, ['Tuesday'])
        self.assertEqual(updated_task.max_intervals, ['09:00-17:00'])
        self.assertEqual(updated_task.all_days, ['Tuesday', 'Wednesday'])
        self.assertEqual(updated_task.difficulty, 8)
        self.assertEqual(updated_task.importance, 9)
        self.assertIsNone(updated_task.fixed_day)
        self.assertIsNone(updated_task.fixed_start_time)
        self.assertIsNone(updated_task.fixed_end_time)

    # Test case for updating a task from not fixed to fixed
    def test_update_not_fixed_to_fixed(self):
        not_fixed_task = Task(
            user_id=1,
            taskname='Not Fixed Task',
            fixed=False,
            duration=60,
            preferred_intervals=['09:00-10:00'],
            preferred_days=['Monday'],
            max_intervals=['08:00-18:00'],
            all_days=['Monday', 'Tuesday'],
            difficulty=5,
            importance=7
        )
        db.session.add(not_fixed_task)
        db.session.commit()

        update_data = {
            'taskname': 'Fixed Task',
            'fixed': True,
            'fixed_day': 'Wednesday',
            'fixed_start_time': '14:00',
            'fixed_end_time': '15:00'
        }
        response = self.app.put(f'/updateTask/{not_fixed_task.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Task updated successfully', response.get_data(as_text=True))

        updated_task = Task.query.get(not_fixed_task.id)
        self.assertEqual(updated_task.taskname, 'Fixed Task')
        self.assertEqual(updated_task.fixed, True)
        self.assertEqual(updated_task.fixed_day, 'Wednesday')
        self.assertEqual(updated_task.fixed_start_time, datetime.strptime('14:00', '%H:%M').time())
        self.assertEqual(updated_task.fixed_end_time, datetime.strptime('15:00', '%H:%M').time())
        self.assertIsNone(updated_task.preferred_intervals)
        self.assertIsNone(updated_task.preferred_days)
        self.assertIsNone(updated_task.max_intervals)
        self.assertIsNone(updated_task.all_days)
        self.assertIsNone(updated_task.difficulty)
        self.assertIsNone(updated_task.importance)

if __name__ == '__main__':
    unittest.main()
