from app import app
from time import sleep

sleep_seconds = 0.1


def _wait(*args, **kwargs):
    if not kwargs:
        for a in args:
            if type(a) is dict:
                kwargs = a
    print(kwargs.get("fixture_name"))
    sleep(sleep_seconds)
    return kwargs.get("fixture_name", "UNKNOWN")

@app.task
def wait(*args, **kwargs):
    return _wait(*args, **kwargs)

@app.task
def low_priority_wait(*args, **kwargs):
    return _wait(*args, **kwargs)

@app.task
def high_priority_wait(*args, **kwargs):
    return _wait(*args, **kwargs)
