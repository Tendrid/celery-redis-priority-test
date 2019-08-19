from unittest import TestCase, mock, skip
from tasks import wait
from time import sleep
from celery import group, chord, chain

# Priorities:   0, 3, 6, 9
# Queues:       a-high, b-medium, c-low, d-ghost


def hook(*args, **kwargs):
    print(args)
    print(kwargs)

class TestPriority(TestCase):

    @skip("")
    def test_simple(self):
        """
        Test a simple FIFO queue with priority (de)escalation
        """
        tasks = [
            { "priority": 0, "fixture_name": "A" },
            { "priority": 0, "fixture_name": "B" },
            { "priority": 0, "fixture_name": "C" },
            { "priority": 9, "fixture_name": "D" }, # deescalate
            { "priority": 0, "fixture_name": "E" },
            { "priority": 0, "fixture_name": "F" },
            { "priority": 9, "fixture_name": "G" }, # deescalate
            { "priority": 0, "fixture_name": "H" },
        ]
        results = [] 
        for task in tasks:
            t = wait.s(**task)
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
            sleep(1)

        self.assertEqual(
            success,
            ["A", "B", "C", "E", "F", "H", "D", "G"],
            "Numeric Priority not completed in expected order"
        )

    @skip("")
    def test_chord(self):
        """
        Test a complex chain of chords with (de)escalation
        """
        tasks_defs = [
            (0, 0),
            (1, 0),
            (2, 9), # deescalate
            (3, 0),
        ]
        results = []
        for task_id, task_priority in tasks_defs:

            _chains = []
            for chain_id in ["A", "B"]:
                chain_tasks = [
                    { "fixture_name": f"{task_id}-{chain_id}-1" },
                    { "fixture_name": f"{task_id}-{chain_id}-2" },
                    { "fixture_name": f"{task_id}-{chain_id}-3" },
                ]
                _c = []
                for task in chain_tasks:
                    _c.append(wait.s(**task))
                _chains.append(chain(_c))
            t = chain(
                wait.s({"prority":task_priority, "fixture_name": f"{task_id}-A"}),
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
            sleep(1)

        self.assertEqual(
            success,
            ["0-C", "1-C", "3-C", "2-C"],
            "Numeric Priority not completed in expected order"
        )



class TestPriorityQueue(TestCase):
    def test_simple(self):
        """
        Test a simple FIFO queue with priority (de)escalation
        """
        tasks = [
            { "priority": 0, "fixture_name": "A", "queue":"a-high"},    # 1
            { "priority": 0, "fixture_name": "B", "queue":"b-medium"},  # 3
            { "priority": 0, "fixture_name": "C", "queue":"a-high"},    # 1
            { "priority": 9, "fixture_name": "D", "queue":"a-high"},    # 2
            { "priority": 0, "fixture_name": "E", "queue":"a-high"},    # 1
            { "priority": 0, "fixture_name": "F", "queue":"b-medium"},  # 3
            { "priority": 9, "fixture_name": "G", "queue":"a-high"},    # 2
            { "priority": 0, "fixture_name": "H", "queue":"a-high"},    # 1
        ]
        results = [] 
        for task in tasks:
            t = wait.s(**task).set(queue=task["queue"])
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
            sleep(1)

        self.assertEqual(
            success,
            ["A", "C", "E", "H", "D", "G", "B", "F"],
            #['A', 'C', 'E', 'H', 'B', 'F', 'D', 'G']
            "Numeric Priority not completed in expected order"
        )