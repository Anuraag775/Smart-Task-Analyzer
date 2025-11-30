from django.test import TestCase
from datetime import date, timedelta
from .scoring import detect_circular_dependencies, compute_dependency_counts, score_task

class ScoringUnitTests(TestCase):
    def test_circular_detection(self):
        tasks = [
            {'id': 1, 'dependencies': [2]},
            {'id': 2, 'dependencies': [3]},
            {'id': 3, 'dependencies': [1]},
        ]
        self.assertTrue(detect_circular_dependencies(tasks))

    def test_dependency_counts(self):
        tasks = [
            {'id': 0, 'dependencies': []},
            {'id': 1, 'dependencies': [0]},
            {'id': 2, 'dependencies': [0,1]},
        ]
        counts = compute_dependency_counts(tasks)
        self.assertEqual(counts[0], 2)
        self.assertEqual(counts[1], 1)
        self.assertEqual(counts[2], 0)

    def test_scoring_overdue_and_defaults(self):
        due = date.today() - timedelta(days=1)
        t = {'id': 0, 'importance': 7, 'due_date': due, 'estimated_hours': 2}
        counts = {0: 0}
        score, explanation = score_task(t, counts)
        self.assertTrue(isinstance(score, float) or isinstance(score, int))
        self.assertIn('Urgency', explanation)
