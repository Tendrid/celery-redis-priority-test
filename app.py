from celery import Celery, signals
from kombu import Queue

app = Celery("priority-test")

app.conf.result_backend = "redis://dev:dev@localhost:6379"
app.conf.broker_url = "redis://dev:dev@localhost:6379"

app.conf.task_default_queue = "b-medium"

app.conf.task_create_missing_queues = True

#app.conf.broker_transport_options = {"queue_order_strategy": "sorted"}

app.conf.worker_prefetch_multiplier = 1


app.conf.task_queues = (
    Queue("a-high", routing_key="a-high"),
    Queue("b-medium", routing_key="b-medium"),
    Queue("c-low", routing_key="c-low"),
    Queue("d-ghost", routing_key="d-ghost"),
)