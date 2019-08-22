from unittest import TestCase, mock, skip
from tasks import wait, low_priority_wait, high_priority_wait, sleep_seconds
from time import sleep
from celery import group, chord, chain


class TestDynamicPriorityRoutes(TestCase):

    """
    def setUp(self):
        for i in range(10):
            t = high_priority_wait.s(fixture_name="QUEUE FILLER")
            t.apply_async(priority=0)
    """

    def test_complex(self):
        """
        Test a complex chain of chords which pins the start tasks
        to a low priority queue.  The raw task output should show
        that these tasks are fired with no children task overlap.

        Note:
        This test proves that app.conf.task_inherit_parent_priority
        works for celery (conflicts with documentation).  To test,
        use -c2 with the celery app cli.  This will result in
        the tasks completing out of order.  If you then set the config
        setting app.conf.task_inherit_parent_priority = True
        and run the task again, you will see the tasks finish
        in the desired order, as expected.
        """
        tasks_defs = [
            ("A", 0),
            ("B", 6),
            ("C", 9),
            ("D", 3),
        ]
        results = []
        for task_id, task_priority in tasks_defs:

            _chains = []
            for chain_id in ["1", "2", "3", "4", "5"]:
                chain_tasks = [
                    { "fixture_name": f"{task_id}-X-{chain_id}-1" },
                    { "fixture_name": f"{task_id}-X-{chain_id}-2" },
                    { "fixture_name": f"{task_id}-X-{chain_id}-3" },
                ]
                _c = []
                for task in chain_tasks:
                    _c.append(high_priority_wait.s(**task))
                _chains.append(chain(_c))
            t = chain(
                low_priority_wait.s({"fixture_name": f"{task_id}-1"}),
                chord(
                    _chains,
                    high_priority_wait.s({"fixture_name": f"{task_id}-2"})
                ),
                high_priority_wait.s({"fixture_name": f"{task_id}-3"}),
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
            ["A-3", "D-3", "B-3", "C-3"],
            "Numeric Priority not completed in expected order"
        )