import unittest
from schedule import get_intersecting_intervals

class TestGetIntersectingIntervals(unittest.TestCase):

    def test_full_overlap(self):
        input_intervals = ['09:00-10:00']
        available_intervals = ['09:00-10:00']
        expected_result = ['09:00-10:00']
        self.assertEqual(get_intersecting_intervals(input_intervals, available_intervals), expected_result)

    def test_partial_overlap(self):
        input_intervals = ['09:00-11:00']
        available_intervals = ['10:00-12:00']
        expected_result = ['10:00-11:00']
        self.assertEqual(get_intersecting_intervals(input_intervals, available_intervals), expected_result)

    def test_no_overlap(self):
        input_intervals = ['09:00-10:00']
        available_intervals = ['10:00-11:00']
        expected_result = []
        self.assertEqual(get_intersecting_intervals(input_intervals, available_intervals), expected_result)

    def test_edge_case_overlap(self):
        input_intervals = ['09:00-10:00']
        available_intervals = ['08:00-09:00', '10:00-11:00']
        expected_result = []
        self.assertEqual(get_intersecting_intervals(input_intervals, available_intervals), expected_result)

    def test_multiple_intervals(self):
        input_intervals = ['09:00-10:00', '11:00-12:00']
        available_intervals = ['08:00-09:30', '10:30-11:30']
        expected_result = ['09:00-09:30', '11:00-11:30']
        self.assertEqual(get_intersecting_intervals(input_intervals, available_intervals), expected_result)

    def test_empty_intervals(self):
        input_intervals = []
        available_intervals = ['08:00-09:30']
        expected_result = []
        self.assertEqual(get_intersecting_intervals(input_intervals, available_intervals), expected_result)

        input_intervals = ['08:00-09:30']
        available_intervals = []
        expected_result = []
        self.assertEqual(get_intersecting_intervals(input_intervals, available_intervals), expected_result)

if __name__ == '__main__':
    unittest.main()