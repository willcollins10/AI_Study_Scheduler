import unittest
from datetime import datetime
from schedule import adjust_intervals

class TestAdjustIntervals(unittest.TestCase):
    
    # Test that we can split in interval
    # beginInterval < start < endInterval
    # beginInterval < end < endInterval
    def test_adjust_intervals_basic(self):
        intervals = ['09:00-12:00']
        start = datetime.strptime('10:00', '%H:%M')
        end = datetime.strptime('11:00', '%H:%M')
        expected = ['09:00-10:00', '11:00-12:00']
        result = adjust_intervals(intervals, start, end)
        assert result == expected

    # start and end time are inbetween the open intervals, so nothing should be changed
    # NOTE: According to scheduling logic this should never happen!!!!
    #NOTE: This test case is just to ensure the functionality of adjust_intervals function
    def test_adjust_intervals_no_overlap(self):
        intervals = ['09:00-10:00', '11:00-12:00']
        start = datetime.strptime('10:00', '%H:%M')
        end = datetime.strptime('11:00', '%H:%M')
        expected = ['09:00-10:00', '11:00-12:00']
        self.assertEqual(adjust_intervals(intervals, start, end), expected)
    
    # Need to slice off the end of intervals
    def test_adjust_intervals_partial_overlap(self):
        intervals = ['09:00-11:00']
        start = datetime.strptime('10:00', '%H:%M')
        end = datetime.strptime('11:00', '%H:%M')
        expected = ['09:00-10:00']
        self.assertEqual(adjust_intervals(intervals, start, end), expected)
    
    # The interval is perfectly overlapped
    def test_adjust_intervals_full_overlap(self):
        intervals = ['09:00-11:00']
        start = datetime.strptime('09:00', '%H:%M')
        end = datetime.strptime('11:00', '%H:%M')
        expected = []
        self.assertEqual(adjust_intervals(intervals, start, end), expected)
    
    def test_adjust_intervals_split_overlap(self):
        intervals = ['09:00-12:00']
        start = datetime.strptime('10:00', '%H:%M')
        end = datetime.strptime('11:00', '%H:%M')
        expected = ['09:00-10:00', '11:00-12:00']
        self.assertEqual(adjust_intervals(intervals, start, end), expected)

if __name__ == '__main__':
    unittest.main()
