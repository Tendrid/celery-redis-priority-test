from celery import Celery
from kombu import Queue

app_name = "priority-test"
app = Celery(app_name)

app.conf.result_backend = app.conf.broker_url = "redis://redis-stream:6379/0"

app.conf.task_default_queue = "b-medium"

app.conf.task_create_missing_queues = True

#app.conf.task_default_priority = 3

app.conf.broker_transport_options = {"queue_order_strategy": "sorted"}

app.conf.worker_prefetch_multiplier = 1

app.conf.task_inherit_parent_priority = True

#app.conf.broker_transport_options = {
#    'priority_steps': list(range(10)),
#}

app.conf.task_queues = (
    Queue("a-high"),
    Queue("b-medium"),
    Queue("c-low"),
)

app.conf.task_routes = {
    'tasks.low_priority_wait': {
        'queue': 'c-low',
        'routing_key': 'c-low.priority',
    },
    'tasks.high_priority_wait': {
        'queue': 'a-high',
        'routing_key': 'a-high.priority',
    },
}
