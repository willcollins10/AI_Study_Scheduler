import unittest
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from schedule import schedule_task, adjust_intervals, find_open_spot


# Create a dummy test class & database for testing purposes
class Task:
    def __init__(self, id, taskname, duration, preferred_intervals=None, preferred_days=None):
        self.id = id
        self.taskname = taskname
        self.duration = duration
        self.preferred_intervals = preferred_intervals
        self.preferred_days = preferred_days

def initialize_schedule(days):
    full_day_interval = ['00:00-23:59']
    schedule = {day: {'tasks': [], 'intervals': full_day_interval} for day in days}
    return schedule

class TestScheduleTask(unittest.TestCase):

    def setUp(self):
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.schedule = initialize_schedule(self.days)

    # Test to ensure we can successfully schedule a task when supposed to 
    def test_successful_scheduling(self):
        task = Task(id=1, taskname='Task 1', duration=60, preferred_intervals=['09:00-11:00'], preferred_days=['Monday', 'Tuesday'])
        schedule, success = schedule_task(self.schedule, task, task.preferred_days, task.preferred_intervals, task.duration)
        
        self.assertTrue(success)
        self.assertEqual(len(schedule['Monday']['tasks']), 1)
        self.assertEqual(schedule['Monday']['tasks'][0]['taskname'], 'Task 1')
        self.assertEqual(schedule['Monday']['tasks'][0]['start_time'], '09:00')
        self.assertEqual(schedule['Monday']['tasks'][0]['end_time'], '10:00')
    # Test to ensure we can't schedule task when to intervals are available
    def test_no_preferred_intervals_available(self):
        # Here the duration > intervals
        task = Task(id=2, taskname='Task 2', duration=120, preferred_intervals=['12:00-13:00'], preferred_days=['Wednesday'])
        schedule, success = schedule_task(self.schedule, task, task.preferred_days, task.preferred_intervals, task.duration)
        
        self.assertFalse(success)
        self.assertEqual(len(schedule['Wednesday']['tasks']), 0)

    # Test to ensrue we can't schedule a day that isn't in the schedule
    # This shouldn't occur based on functionality of app, but good to have
    def test_day_not_in_schedule(self):
        task = Task(id=3, taskname='Task 3', duration=30, preferred_intervals=['09:00-09:30'], preferred_days=['Sunday'])
        schedule, success = schedule_task(self.schedule, task, task.preferred_days, task.preferred_intervals, task.duration)
        
        self.assertFalse(success)
        self.assertNotIn('Sunday', schedule)
    # Test when the duration is longer than a day itself (similar to above test)
    def test_task_duration_longer_than_any_interval(self):
        task = Task(id=4, taskname='Task 4', duration=1440, preferred_intervals=['00:00-23:59'], preferred_days=['Friday'])
        schedule, success = schedule_task(self.schedule, task, task.preferred_days, task.preferred_intervals, task.duration)
        
        self.assertFalse(success)
        self.assertEqual(len(schedule['Friday']['tasks']), 0)

     # Test to ensure a task can be partially scheduled within preferred intervals and extends beyond
    def test_task_partially_fitting_within_intervals(self):
        # Create a task with a duration that partially fits within the preferred interval
        task = Task(id=5, taskname='Task 5', duration=60, preferred_intervals=['09:00-11:00'], preferred_days=['Monday'])
        # Attempt to schedule the task
        schedule, success = schedule_task(self.schedule, task, task.preferred_days, task.preferred_intervals, task.duration)
        
        # Check if the task was successfully scheduled
        self.assertTrue(success)
        # Verify that the task was added to the schedule on Monday
        self.assertEqual(len(schedule['Monday']['tasks']), 1)
        self.assertEqual(schedule['Monday']['tasks'][0]['taskname'], 'Task 5')
        # Verify the start and end times of the task
        self.assertEqual(schedule['Monday']['tasks'][0]['start_time'], '09:00')
        self.assertEqual(schedule['Monday']['tasks'][0]['end_time'], '10:00')
    
    def test_schedule_multiple_task_same_day(self):
        task1 = Task(id=6, taskname='Task 6', duration=60, preferred_intervals=['09:00-10:00'], preferred_days=['Monday'])
        task2 = Task(id=7, taskname='Task 7', duration=60, preferred_intervals=['09:00-10:00'], preferred_days=['Monday'])
        task3 = Task(id=8, taskname='Task 8', duration=60, preferred_intervals=['12:00-13:00'], preferred_days=['Monday'])

        schedule, success1 = schedule_task(self.schedule, task1, task1.preferred_days, task1.preferred_intervals, task1.duration)
        self.assertTrue(success1)
        self.assertEqual(len(schedule['Monday']['tasks']), 1)
        self.assertEqual(schedule['Monday']['tasks'][0]['taskname'], 'Task 6')

        schedule, success2 = schedule_task(self.schedule, task2, task2.preferred_days, task2.preferred_intervals, task2.duration)
        self.assertFalse(success2)
        self.assertEqual(len(schedule['Monday']['tasks']), 1)
        self.assertEqual(schedule['Monday']['tasks'][0]['taskname'], 'Task 6')

        schedule, success3 = schedule_task(self.schedule, task3, task3.preferred_days, task3.preferred_intervals, task3.duration)
        self.assertTrue(success3)
        self.assertEqual(len(schedule['Monday']['tasks']), 2)
        self.assertEqual(schedule['Monday']['tasks'][0]['taskname'], 'Task 6')
        self.assertEqual(schedule['Monday']['tasks'][1]['taskname'], 'Task 8')
    
    def test_overlap_preferred_intervals(self):
        task1 = Task(id=6, taskname='Task 6', duration=60, preferred_intervals=['09:00-11:00'], preferred_days=['Monday'])
        task2 = Task(id=7, taskname='Task 7', duration=60, preferred_intervals=['09:00-11:00'], preferred_days=['Monday'])

        schedule, success1 = schedule_task(self.schedule, task1, task1.preferred_days, task1.preferred_intervals, task1.duration)
        schedule, success2 = schedule_task(self.schedule, task2, task2.preferred_days, task2.preferred_intervals, task2.duration)

        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertEqual(len(schedule['Monday']['tasks']), 2)
        self.assertEqual(schedule['Monday']['tasks'][0]['taskname'], 'Task 6')
        self.assertEqual(schedule['Monday']['tasks'][1]['taskname'], 'Task 7')
        self.assertEqual(schedule['Monday']['tasks'][0]['start_time'], '09:00')
        self.assertEqual(schedule['Monday']['tasks'][0]['end_time'], '10:00')
        self.assertEqual(schedule['Monday']['tasks'][1]['start_time'], '10:00')
        self.assertEqual(schedule['Monday']['tasks'][1]['end_time'], '11:00')
        

if __name__ == '__main__':
    unittest.main()
