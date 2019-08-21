from unittest import TestCase, mock, skip
from tasks import wait, low_priority_wait, high_priority_wait, sleep_seconds
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


    def test_complex(self):
        """
        Test a complex chain of chords with (de)escalation
        This test further prooves what TestPriorityQueue.test_simple
        already states in its comment, but tests it further.
        """
        tasks_defs = [
            (0, 0, high_priority_wait),
            (1, 3, low_priority_wait),
            (2, 3, high_priority_wait),
            (3, 6, low_priority_wait),
        ]
        results = []
        for task_id, task_priority, task in tasks_defs:

            _chains = []
            for chain_id in ["A", "B"]:
                chain_fixtures = [
                    f"{task_id}-{chain_id}-1",
                    f"{task_id}-{chain_id}-2",
                    f"{task_id}-{chain_id}-3",
                ]
                _c = []
                for fixture_name in chain_fixtures:
                    _c.append(wait.s(fixture_name=fixture_name))
                _chains.append(chain(_c))
            t = chain(
                task.s({"prority":task_priority, "fixture_name": f"{task_id}-A"}),
                chord(
                    _chains,
                    wait.s({"prority":task_priority, "fixture_name": f"{task_id}-B"})
                ),
                wait.s({"prority":task_priority, "fixture_name": f"{task_id}-C"}),
            )
            results.append(t.apply_async(priority=task_priority))

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
            ["0-C", "2-C", "1-C", "3-C"],
            "Numeric Priority not completed in expected order"
        )