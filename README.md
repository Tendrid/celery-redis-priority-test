# celery-redis-priority-test
Used to determine how priorities are working in celery with a redis backend



celery worker -A tasks -Q a-high,b-medium,c-low,d-ghost -Ofair -c1 --prefetch-multiplier=1
