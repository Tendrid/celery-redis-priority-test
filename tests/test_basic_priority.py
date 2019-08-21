from unittest import TestCase, mock, skip
from tasks import wait, sleep_seconds
from time import sleep
from celery import group, chord, chain

# Priorities:   0, 3, 6, 9
# Queues:       a-high, b-medium, c-low


"""
NOTE:
This first task fired in each test must ALWAYS assumed to finish first. This
is because when the tasks fire, the queue is empty, so it has no other higher priority
"""

class TestPriority(TestCase):

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
            sleep(sleep_seconds)

        self.assertEqual(
            success,
            ["A", "B", "C", "E", "F", "H", "D", "G"],
            "Numeric Priority not completed in expected order"
        )

    def test_complex(self):
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
            sleep(sleep_seconds)

        self.assertEqual(
            success,
            ["0-C", "1-C", "3-C", "2-C"],
            "Numeric Priority not completed in expected order"
        )



class TestPriorityQueue(TestCase):
    def test_simple(self):
        """
        Test a simple FIFO queue with priority (de)escalation

        This test shows that priority is honored above queue order
        eg: given two queues, "a-work" and "b-work", and 3 tasks,
        "t-1", "t-2", and "t-3", if t-1 and t-2 are in a, and t3 is in b,
        they will complete in order (t1,t2,t3)

        However, if t-2 has a priority of 0, and all others have a priority of 3,
        they will complete: t-2, t-1, t-3

        Further, if t-3 has a priority of 0, and t-1 and t-2 have a priority of 3,
        they will complete: t-3, t-1, t-2
        """
        tasks = [
            { "priority": 0, "fixture_name": "A", "queue":"a-high"},
            { "priority": 0, "fixture_name": "B", "queue":"b-medium"},
            { "priority": 9, "fixture_name": "C", "queue":"b-medium"},
            { "priority": 3, "fixture_name": "D", "queue":"a-high"},
            { "priority": 3, "fixture_name": "E", "queue":"a-high"},
            { "priority": 3, "fixture_name": "F", "queue":"b-medium"},
            { "priority": 3, "fixture_name": "G", "queue":"a-high"},
            { "priority": 9, "fixture_name": "H", "queue":"a-high"},
        ]
        results = [] 
        for task in tasks:
            t = wait.s(**task)
            results.append(t.apply_async(priority=task["priority"], queue=task["queue"]))

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
        There are, however, interesting things to note in the output
        such as task 0-C sometimes completing _after_ 2-A beings.
        """
        tasks_defs = [
            (0, 0, "a-high"),
            (1, 3, "c-low"),
            (2, 3, "a-high"),
            (3, 6, "c-low"),
        ]
        results = []
        for task_id, task_priority, queue in tasks_defs:

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
            results.append(t.apply_async(priority=task_priority, queue=queue))

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