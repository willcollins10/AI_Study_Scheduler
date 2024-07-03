import unittest
from app import app,db
from model import Task
from test_config import TestConfig


# Going to have to work on testing with many intervals
# This test case just has one interval in preferred_intervals & max_intervals that get changed
class UpdateTaskTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object(TestConfig)
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

     # Add a sample task to the database
        self.task = Task(
            user_id=1,
            taskname='Original Task',
            fixed=False,
            duration=60,
            preferred_intervals=['09:00-10:00'],
            preferred_days=['Monday'],
            max_intervals=['08:00-18:00'],
            all_days=['Monday', 'Tuesday'],
            difficulty=5,
            importance=7,
        )
        db.session.add(self.task)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Updates all fields of a task
    # Checks that the status response code is 200
    # Verifies that the task's attributes are correctly updated in the database
    def test_update_task_success(self):
        update_data = {
            'taskname': 'Updated Task',
            'fixed': False,
            'duration': 90,
            'preferred_intervals': ['10:00-11:00'],
            'preferred_days': ['Tuesday'],
            'max_intervals': ['09:00-17:00'],
            'all_days': ['Tuesday', 'Wednesday'],
            'difficulty': 8,
            'importance': 9
        }
        # Check for 200 response code
        response = self.app.put(f'/updateTask/{self.task.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Task updated successfully', response.get_data(as_text=True))

        # Verify that the tasks are correctly updated in the database
        updated_task = Task.query.get(self.task.id)
        self.assertEqual(updated_task.taskname, update_data['taskname'])
        self.assertEqual(updated_task.fixed, update_data['fixed'])
        self.assertEqual(updated_task.duration, update_data['duration'])
        self.assertEqual(updated_task.preferred_intervals, update_data['preferred_intervals'])
        self.assertEqual(updated_task.preferred_days, update_data['preferred_days'])
        self.assertEqual(updated_task.max_intervals, update_data['max_intervals'])
        self.assertEqual(updated_task.all_days, update_data['all_days'])
        self.assertEqual(updated_task.difficulty, update_data['difficulty'])
        self.assertEqual(updated_task.importance, update_data['importance'])

    # Tries to update a task that doesn't exist
    # Making sure we get the 404 response status code
    def test_update_task_not_found(self):
        response = self.app.put('/updateTask/9999', json={
            'taskname': 'Non-existent Task',
            'fixed': True
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn('Task not found', response.get_data(as_text=True))

    # Only updates some fields of the task
    # We are just updating taskname & duration
    def test_update_task_partial_update(self):
        update_data = {
            'taskname': 'Partially Updated Task',
            'fixed': False,
            'duration': 45
        }
        response = self.app.put(f'/updateTask/{self.task.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Task updated successfully', response.get_data(as_text=True))

        updated_task = Task.query.get(self.task.id)
        self.assertEqual(updated_task.taskname, update_data['taskname'])
        self.assertEqual(updated_task.duration, update_data['duration'])
        self.assertEqual(updated_task.fixed, self.task.fixed)  # unchanged field
        self.assertEqual(updated_task.preferred_intervals, self.task.preferred_intervals)  # unchanged field
        self.assertEqual(updated_task.preferred_days, self.task.preferred_days)  # unchanged field
    
    def test_update_task_invalid_taskname(self):
         response = self.app.put(f'/updateTask/{self.task.id}', json={
             'taskname': 123  # invalid type
         })
         self.assertEqual(response.status_code, 400)
         self.assertIn('Invalid data: taskname must be a str', response.get_data(as_text=True))

    def test_update_task_invalid_fixed(self):
         response = self.app.put(f'/updateTask/{self.task.id}', json={
              'fixed': 'yes'  # invalid type
          })
         self.assertEqual(response.status_code, 400)
         self.assertIn('Invalid data: fixed must be a bool', response.get_data(as_text=True))
         

    def test_update_task_invalid_duration(self):
        response = self.app.put(f'/updateTask/{self.task.id}', json={
            'duration': 'invalid'  # invalid type
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid data: duration must be a int', response.get_data(as_text=True))

    def test_update_task_invalid_preferred_intervals(self):
        response = self.app.put(f'/updateTask/{self.task.id}', json={
            'preferred_intervals': 'invalid'  # invalid type
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid data: preferred_intervals must be a list', response.get_data(as_text=True))

    def test_update_task_invalid_preferred_days(self):
        response = self.app.put(f'/updateTask/{self.task.id}', json={
            'preferred_days': 'invalid'  # invalid type
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid data: preferred_days must be a list', response.get_data(as_text=True))

    def test_update_task_invalid_max_intervals(self):
        response = self.app.put(f'/updateTask/{self.task.id}', json={
            'max_intervals': 'invalid'  # invalid type
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid data: max_intervals must be a list', response.get_data(as_text=True))

    def test_update_task_invalid_all_days(self):
        response = self.app.put(f'/updateTask/{self.task.id}', json={
            'all_days': 'invalid'  # invalid type
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid data: all_days must be a list', response.get_data(as_text=True))

    def test_update_task_invalid_difficulty(self):
         response = self.app.put(f'/updateTask/{self.task.id}', json={
            'difficulty': 'invalid'  # invalid type
         })
         self.assertEqual(response.status_code, 400)
         self.assertIn('Invalid data: difficulty must be a int', response.get_data(as_text=True))

    def test_update_task_invalid_importance(self):
         response = self.app.put(f'/updateTask/{self.task.id}', json={
             'importance': 'invalid'  # invalid type
         })
         self.assertEqual(response.status_code, 400)
         self.assertIn('Invalid data: importance must be a int', response.get_data(as_text=True))

