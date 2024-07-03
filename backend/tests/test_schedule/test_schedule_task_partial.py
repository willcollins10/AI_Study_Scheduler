import unittest
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from schedule import schedule_task_partial, adjust_intervals, find_open_spot
from model import db

# Dummy Task class with necessary data so don't interact with database
class Task:
    def __init__(self, id, taskname, duration, preferred_intervals=None, preferred_days=None, max_intervals=None):
        self.id = id
        self.taskname = taskname
        self.duration = duration
        self.preferred_intervals = preferred_intervals
        self.preferred_days = preferred_days
        self.max_intervals = max_intervals

def initialize_schedule(days):
    full_day_interval = ['00:00-23:59']
    schedule = {day: {'tasks': [], 'intervals': full_day_interval} for day in days}
    return schedule

class TestScheduleTaskPartial(unittest.TestCase):
    def setUp(self):
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.schedule = initialize_schedule(self.days)
    
    
    def test_partial_scheduling_within_max_intervals(self):
        """
        Test scheduling a task that partially fits within preferred interval and extends into max interval.
        """
        task = Task(id=2, taskname='Task 2', duration=60, preferred_intervals=['09:00-10:00'], preferred_days=['Monday'], max_intervals=['08:00-11:00'])
        self.schedule['Monday']['intervals'] = ['08:00-08:30', '09:15-11:00']  # Open intervals
        
        schedule, success = schedule_task_partial(self.schedule, task, task.preferred_days, task.preferred_intervals, task.max_intervals, task.duration)
        
        self.assertTrue(success)
        self.assertEqual(len(schedule['Monday']['tasks']), 1)
        self.assertEqual(schedule['Monday']['tasks'][0]['taskname'], 'Task 2')
        self.assertEqual(schedule['Monday']['tasks'][0]['start_time'], '09:15')
        self.assertEqual(schedule['Monday']['tasks'][0]['end_time'], '10:15')

    def test_task_cannot_be_scheduled(self):
        task = Task(id=3, taskname='Task 3', duration=60, preferred_intervals=['09:00-10:00'], preferred_days=['Monday'], max_intervals=['08:00-11:00'])
        self.schedule['Monday']['intervals'] = []  # No open intervals
        
        schedule, success = schedule_task_partial(self.schedule, task, task.preferred_days, task.preferred_intervals, task.max_intervals, task.duration)
        
        self.assertFalse(success)
        self.assertEqual(len(schedule['Monday']['tasks']), 0)

    # Should return false because there is no overlap with preferred_intvals and UNIOn of available_intervals and max_intervals
    def test_task_fits_completely_within_max_intervals_but_empty_intersection(self):
        task = Task(id=4, taskname='Task 4', duration=60, preferred_intervals=['09:00-10:00'], preferred_days=['Monday'], max_intervals=['08:00-11:00'])
        self.schedule['Monday']['intervals'] = ['08:00-09:00', '10:00-11:00']  # Open intervals
        
        schedule, success = schedule_task_partial(self.schedule, task, task.preferred_days, task.preferred_intervals, task.max_intervals, task.duration)
        
        self.assertFalse(success)
        self.assertEqual(len(schedule['Monday']['tasks']), 0)



    def test_day_not_in_schedule(self):
        task = Task(id=8, taskname='Task 8', duration=60, preferred_intervals=['09:00-10:00'], preferred_days=['Sunday'], max_intervals=['08:00-11:00'])
        
        schedule, success = schedule_task_partial(self.schedule, task, task.preferred_days, task.preferred_intervals, task.max_intervals, task.duration)
        
        self.assertFalse(success)
        self.assertNotIn('Sunday', schedule)


    def test_task_almost_available(self):
        task = Task(id=6, taskname='Task 6', duration=90, preferred_intervals=['09:00-10:00'], preferred_days=['Monday'], max_intervals=['08:00-11:00'])
        self.schedule['Monday']['intervals'] = ['08:00-09:15', '09:20-10:15']  # Open intervals
        
        schedule, success = schedule_task_partial(self.schedule, task, task.preferred_days, task.preferred_intervals, task.max_intervals, task.duration)
        
        self.assertFalse(success)
    
    # Testing when the available intervals for that day don't accomadate the task
    def test_task_does_not_fit_within_any_interval(self):
        task = Task(id=7, taskname='Task 7', duration=60, preferred_intervals=['09:00-10:00'], preferred_days=['Monday'], max_intervals=['08:00-09:00'])
        self.schedule['Monday']['intervals'] = ['08:00-08:30']  # Open intervals
        
        schedule, success = schedule_task_partial(self.schedule, task, task.preferred_days, task.preferred_intervals, task.max_intervals, task.duration)
        
        self.assertFalse(success)
        self.assertEqual(len(schedule['Monday']['tasks']), 0)
    
    def test_empty_union_between_max_interval_and_available_interval(self):
        task = Task(id=9, taskname='Task 9', duration=60, preferred_intervals=['09:00-10:00'], preferred_days=['Monday'], max_intervals=['08:00-10:00'])
        self.schedule['Monday']['intervals'] = ['13:00-19:00']

        schedule, success = schedule_task_partial(self.schedule, task, task.preferred_days, task.preferred_intervals, task.max_intervals, task.duration)
        self.assertFalse(success)
        self.assertEqual(len(schedule['Monday']['tasks']), 0)

    def test_task_spans_across_multiple_days(self):
        task = Task(id=10, taskname='Task 10', duration=120, preferred_intervals=['23:00-00:00'], preferred_days=['Monday'], max_intervals=['23:00-01:00'])
        self.schedule['Monday']['intervals'] = ['23:00-23:59']
        self.schedule['Tuesday']['intervals'] = ['00:00-01:00']
        
        schedule, success = schedule_task_partial(self.schedule, task, task.preferred_days, task.preferred_intervals, task.max_intervals, task.duration)
        
        self.assertFalse(success)
        self.assertEqual(len(schedule['Monday']['tasks']), 0)
        self.assertEqual(len(schedule['Tuesday']['tasks']), 0)
    
    def test_schedule_many_tasks_same_day(self):
        task1 = Task(id=10, taskname='Task 10', duration=60, preferred_intervals=['09:00-10:00'], preferred_days=['Monday'], max_intervals=['08:00-11:00'])
        task2 = Task(id=11, taskname='Task 11', duration=60, preferred_intervals=['09:00-10:00'], preferred_days=['Monday'], max_intervals=['08:00-11:00'])
        task3 = Task(id=12, taskname='Task 12', duration=30, preferred_intervals=['09:00-10:00'], preferred_days=['Monday'], max_intervals=['08:00-11:00'])

    



if __name__ == '__main__':
    unittest.main(buffer=False)