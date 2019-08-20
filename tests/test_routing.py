from unittest import TestCase, mock, skip
from tasks import low_priority_wait, high_priority_wait, sleep_seconds
from time import sleep
from celery import group, chord, chain

# Priorities:   0, 3, 6, 9
# Queues:       a-high, b-medium, c-low

class TestPriorityRoutes(TestCase):

    def test_basic_routing(self):
        """
        This test mimics the test in test_basic_priority.TestPriorityQueue.test_simple
        but instead of passing in the queue, it leverages task_routes bound to the app
        """
        tasks = [
            { "priority": 0, "fixture_name": "A", "task": high_priority_wait},
            { "priority": 0, "fixture_name": "B", "task": low_priority_wait},
            { "priority": 9, "fixture_name": "C", "task": low_priority_wait},
            { "priority": 3, "fixture_name": "D", "task": high_priority_wait},
            { "priority": 3, "fixture_name": "E", "task": high_priority_wait},
            { "priority": 3, "fixture_name": "F", "task": low_priority_wait},
            { "priority": 3, "fixture_name": "G", "task": high_priority_wait},
            { "priority": 9, "fixture_name": "H", "task": high_priority_wait},
        ]
        results = [] 
        for task in tasks:
            t = task["task"].s(fixture_name=task["fixture_name"])
            results.append(t.apply_async(priority=task["priority"]))

        complete = False
        success = []
        while not complete:
            complete = True
            for r in results:
                if r.state != "SUCCESS":
                    complete = False
                else:
                    v = r.result
                    if v not in success:
                        success.append(v)
            sleep(sleep_seconds)

        self.assertEqual(
            success,
            ["A", "B", "D", "E", "G", "F", "H", "C"],
            "Numeric Priority not completed in expected order"
        )

