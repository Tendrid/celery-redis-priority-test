from unittest import TestCase, mock, skip
from tasks import wait
from time import sleep

# Priorities:   0, 3, 6, 9
# Queues:       a-high, b-medium, c-low, d-ghost

class TestPriority(TestCase):
    def test_simple(self):
        tasks = [
            { "priority": 0, "fixture_name": "A" },
            { "priority": 0, "fixture_name": "B" },
            { "priority": 0, "fixture_name": "C" },
            { "priority": 9, "fixture_name": "D" },
            { "priority": 0, "fixture_name": "E" },
            { "priority": 0, "fixture_name": "F" },
            { "priority": 0, "fixture_name": "G" },
            { "priority": 9, "fixture_name": "H" },
        ]
        results = [] 
        for task in tasks:
            t = wait.s(**task)
            results.append(t.apply_async(priority=task["priority"]))

        complete = False
        success = []
        while not complete:
            complete = True
            running = False
            for r in results:
                if r.state != "SUCCESS":
                    complete = False
                else:
                    v = r.get()
                    if v not in success:
                        success.append(v)
            sleep(1)

        self.assertEqual(
            success,
            ["A", "B", "C", "E", "F", "G", "D", "H"],
            "Numeric Priority not completed in expected order"
        )