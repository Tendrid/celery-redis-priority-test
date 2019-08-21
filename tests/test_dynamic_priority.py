from unittest import TestCase, mock, skip
from tasks import wait, low_priority_wait, high_priority_wait, sleep_seconds
from time import sleep
from celery import group, chord, chain


class TestDynamicPriorityRoutes(TestCase):

    def test_complex(self):
        """
        Test a complex chain of chords which pins the start tasks
        to a low priority queue.  The raw task output should show
        that these tasks are fired with no children task overlap.
        """
        tasks_defs = [
            (0, 0),
            (1, 6),
            (2, 9),
            (3, 3),
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
                    _c.append(high_priority_wait.s(**task))
                _chains.append(chain(_c))
            t = chain(
                high_priority_wait.s({"prority":task_priority, "fixture_name": f"{task_id}-A"}),
                chord(
                    _chains,
                    high_priority_wait.s({"prority":task_priority, "fixture_name": f"{task_id}-B"})
                ),
                low_priority_wait.s({"prority":task_priority, "fixture_name": f"{task_id}-C"}),
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
            ["0-C", "3-C", "1-C", "2-C"],
            "Numeric Priority not completed in expected order"
        )