import unittest
from datetime import datetime

# Assuming the function is imported from the module where it's defined
from schedule import find_open_spot

class TestFindOpenSpot(unittest.TestCase):

    # When there is an exact match for interval & duration
    def test_find_open_spot_exact_match(self):
        intervals = ['09:00-10:00', '10:00-11:00']
        duration = 60
        start, end = find_open_spot(intervals, duration)
        self.assertEqual(start, datetime.strptime('09:00', '%H:%M'))
        self.assertEqual(end, datetime.strptime('10:00', '%H:%M'))
    
    # When there is a spot that has a longer interval than duration
    def test_find_open_spot_longer_interval(self):
        intervals = ['09:00-11:00', '11:00-12:00']
        duration = 60
        start, end = find_open_spot(intervals, duration)
        self.assertEqual(start, datetime.strptime('09:00', '%H:%M'))
        self.assertEqual(end, datetime.strptime('11:00', '%H:%M'))
    
    # When an one interval is too short, but another is good
    def test_find_open_spot_shorter_interval(self):
        intervals = ['09:00-09:30', '10:00-11:00']
        duration = 60
        start, end = find_open_spot(intervals, duration)
        self.assertEqual(start, datetime.strptime('10:00', '%H:%M'))
        self.assertEqual(end, datetime.strptime('11:00', '%H:%M'))
    
    # When there is no match
    def test_find_open_spot_no_match(self):
        intervals = ['09:00-09:30', '09:45-10:15']
        duration = 60
        start, end = find_open_spot(intervals, duration)
        self.assertIsNone(start)
        self.assertIsNone(end)
    
    # When multiple intervals can fit, you choose the first one
    def test_find_open_spot_exact_multiple_intervals(self):
        intervals = ['09:00-09:30', '10:00-11:00', '12:00-13:00']
        duration = 60
        start, end = find_open_spot(intervals, duration)
        self.assertEqual(start, datetime.strptime('10:00', '%H:%M'))
        self.assertEqual(end, datetime.strptime('11:00', '%H:%M'))

    def test_find_open_spot_partial_fit(self):
        intervals = ['09:00-09:30', '10:00-10:45', '11:00-12:00']
        duration = 30
        start, end = find_open_spot(intervals, duration)
        self.assertEqual(start, datetime.strptime('09:00', '%H:%M'))
        self.assertEqual(end, datetime.strptime('09:30', '%H:%M'))
    

if __name__ == '__main__':
    unittest.main()
