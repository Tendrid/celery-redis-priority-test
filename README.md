# celery-redis-priority-test
Used to determine how priorities are working in celery with a redis backend


# How to do the thing:
run celery in one shell
`celery worker -A tasks -Q a-high,b-medium,c-low,d-ghost -Ofair -c1 --prefetch-multiplier=1`

and run tests in another
`green`
(i dont have pytest commented yet.  will do soon)