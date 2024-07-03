import unittest
from datetime import datetime
from schedule import load_tasks, initialize_schedule, schedule_fixed_tasks, sort_nonfix_tasks
from model import Task, db
from app import app

class TestSchedule(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory SQLite database for testing
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_load_tasks(self):
        # Add test tasks to database
        task1 = Task(user_id=1, taskname='Task 1', fixed=True, duration=60, fixed_day='Monday', fixed_start_time='10:00', fixed_end_time='11:00')
        task2 = Task(user_id=1, taskname='Task 2', fixed=False, duration=60, importance=5, difficulty=3, preferred_days=['Monday'], preferred_intervals=['12:00-13:00'])
        db.session.add(task1)
        db.session.add(task2)
        db.session.commit()

        fixed_tasks, non_fixed_tasks = load_tasks()
        self.assertEqual(len(fixed_tasks), 1)
        self.assertEqual(len(non_fixed_tasks), 1)

    def test_initialize_schedule(self):
        days = ['Monday', 'Tuesday']
        schedule, unschedulable_tasks = initialize_schedule(days)
        self.assertEqual(len(schedule), 2)
        self.assertEqual(len(unschedulable_tasks), 0)
        for day in days:
            # Confirm day is in schedule
            self.assertIn(day, schedule)
            # Confirm tasks init to empty array
            self.assertEqual(schedule[day]['tasks'], [])
            # Confirm each interval for each day is 24hrs
            self.assertEqual(schedule[day]['intervals'], ['0:00-23:59'])
    
    def test_schedule_fixed_tasks(self):
        fixed_tasks = [
            Task(
                user_id=1,
                taskname='Task 1',
                fixed=True,
                duration=60,  # Even though duration is not used for fixed tasks, it must be set
                preferred_intervals=None,
                preferred_days=None,
                max_intervals=None,
                all_days=None,
                difficulty=0,
                importance=0,
                fixed_day='Monday',
                fixed_start_time=datetime.strptime('09:00', '%H:%M').time(),
                fixed_end_time=datetime.strptime('10:00', '%H:%M').time()
            )
        ]
        schedule, unschedulable_tasks = initialize_schedule(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        schedule = schedule_fixed_tasks(schedule, fixed_tasks)

        self.assertEqual(len(schedule['Monday']['tasks']), 1)
        self.assertEqual(schedule['Monday']['tasks'][0]['taskname'], 'Task 1')
        self.assertEqual(schedule['Monday']['tasks'][0]['start_time'], '09:00')
        self.assertEqual(schedule['Monday']['tasks'][0]['end_time'], '10:00')


    def test_sort_nonfix_tasks(self):
        tasks = [
            Task(taskname='Task 1', importance=2, difficulty=3),
            Task(taskname='Task 2', importance=3, difficulty=2),
            Task(taskname='Task 3', importance=1, difficulty=5)
        ]
        sorted_tasks = sort_nonfix_tasks(tasks)
        self.assertEqual(sorted_tasks[0].taskname, 'Task 2')
        self.assertEqual(sorted_tasks[1].taskname, 'Task 1')


if __name__ == '__main__':
    unittest.main()
