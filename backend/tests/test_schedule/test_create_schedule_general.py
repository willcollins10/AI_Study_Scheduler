import unittest
from datetime import datetime
from schedule import create_schedule
from model import db, Task, Schedule, UnschedulableTask
from app import app

class TestCreateScheduleGeneral(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Add some sample data for fixed and non-fixed tasks
        self.sample_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def sample_data(self):
        # Fixed tasks
        fixed_task1 = Task(
            user_id=1,
            taskname='Fixed Task 1',
            fixed=True,
            duration=60,
            fixed_day='Monday',
            fixed_start_time=datetime.strptime('09:00', '%H:%M').time(),
            fixed_end_time=datetime.strptime('10:00', '%H:%M').time()
        )
        fixed_task2 = Task(
            user_id=1,
            taskname='Fixed Task 2',
            fixed=True,
            duration=120,
            fixed_day='Tuesday',
            fixed_start_time=datetime.strptime('10:00', '%H:%M').time(),
            fixed_end_time=datetime.strptime('12:00', '%H:%M').time()
        )

        # Non-fixed tasks
        non_fixed_task1 = Task(
            user_id=1,
            taskname='Non-Fixed Task 1',
            fixed=False,
            duration=90,
            importance=5,
            difficulty=3,
            preferred_intervals=['09:00-11:00'],
            preferred_days=['Wednesday']
        )
        non_fixed_task2 = Task(
            user_id=1,
            taskname='Non-Fixed Task 2',
            fixed=False,
            duration=60,
            importance=3,
            difficulty=2,
            preferred_intervals=['14:00-15:00'],
            preferred_days=['Thursday'],
            max_intervals=['12:00-18:00']
        )

        db.session.add_all([fixed_task1, fixed_task2, non_fixed_task1, non_fixed_task2])
        db.session.commit()

    def test_create_schedule_with_fixed_and_non_fixed_tasks(self):
        # Call create_schedule function
        schedule, unschedulable = create_schedule()

        # Check if fixed tasks are scheduled correctly
        self.assertEqual(len(schedule['Monday']['tasks']), 1)
        self.assertEqual(schedule['Monday']['tasks'][0]['taskname'], 'Fixed Task 1')
        self.assertEqual(schedule['Monday']['tasks'][0]['start_time'], '09:00')
        self.assertEqual(schedule['Monday']['tasks'][0]['end_time'], '10:00')

        self.assertEqual(len(schedule['Tuesday']['tasks']), 1)
        self.assertEqual(schedule['Tuesday']['tasks'][0]['taskname'], 'Fixed Task 2')
        self.assertEqual(schedule['Tuesday']['tasks'][0]['start_time'], '10:00')
        self.assertEqual(schedule['Tuesday']['tasks'][0]['end_time'], '12:00')

        # Check if non-fixed tasks are scheduled correctly
        self.assertEqual(len(schedule['Wednesday']['tasks']), 1)
        self.assertEqual(schedule['Wednesday']['tasks'][0]['taskname'], 'Non-Fixed Task 1')

        self.assertEqual(len(schedule['Thursday']['tasks']), 1)
        self.assertEqual(schedule['Thursday']['tasks'][0]['taskname'], 'Non-Fixed Task 2')

        # Check if there are no unschedulable tasks
        self.assertEqual(len(unschedulable), 0)

    def test_unschedulable_tasks(self):
        # Add a task that cannot be scheduled
        unschedulable_task = Task(
            user_id=1,
            taskname='Unschedulable Task',
            fixed=False,
            duration=300,
            importance=4,
            difficulty=3,
            preferred_intervals=['08:00-08:30'],
            preferred_days=['Monday']
        )
        db.session.add(unschedulable_task)
        db.session.commit()

        # Call create_schedule function
        schedule, unschedulable = create_schedule()

        # Check if unschedulable task is added to unschedulable list
        self.assertEqual(len(unschedulable), 1)
        self.assertEqual(unschedulable[0].taskname, 'Unschedulable Task')

if __name__ == '__main__':
    unittest.main()
