#### celery-redis-priority-test
Used to determine how priorities are working in celery with a redis backend


#### How to do the thing:
###### run celery in one shell
`celery worker -A tasks -Q a-high,b-medium,c-low -Ofair -c1 --prefetch-multiplier=1`

###### and run tests in another
`green`

(i dont have pytest commented yet.  will do soon)


#### Undocumented, or incorrect assertions of Celery and Redis:
1. `task_inherit_parent_priority` is available for the Redis backend, and not just AMQP
2. Task priority order is low numeric value to high numeric value, eg: tasks with a priority of `0` are handeled _before_ `9`
3. If you set the `broker_transport_options` to `{"queue_order_strategy": "sorted"}`, it will prioritize tasks from queues in alphabetical order
4. Tasks are ran in order of sorting first by task priority, and second by queue order 
