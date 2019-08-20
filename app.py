from celery import Celery, signals
from kombu import Queue, Exchange

app = Celery("priority-test")

app.conf.result_backend = "redis://dev:dev@localhost:6379"
app.conf.broker_url = "redis://dev:dev@localhost:6379"

app.conf.task_default_queue = "b-medium"

app.conf.task_create_missing_queues = True

#app.conf.task_default_priority = 3

app.conf.broker_transport_options = {"queue_order_strategy": "sorted"}

app.conf.worker_prefetch_multiplier = 1

#app.conf.broker_transport_options = {
#    'priority_steps': list(range(10)),
#}

app.conf.task_queues = (
    Queue("a-high"),
    Queue("b-medium"),
    Queue("c-low"),
    Queue("d-ghost"),
)

"""
app.conf.task_queues = (
    Queue('a-high', Exchange('default'), routing_key='a-high'),
    Queue('b-medium',  Exchange('default'),   routing_key='b-medium'),
    Queue('c-low',  Exchange('default'),   routing_key='c-low'),
    Queue('d-ghost',  Exchange('default'),   routing_key='d-ghost'),
)

app.conf.task_default_queue = 'default'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'default'
"""