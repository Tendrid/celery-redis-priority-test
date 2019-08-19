from app import app
from time import sleep

sleep_seconds = 1

@app.task
def wait(priority, fixture_name):
    print(f"IN  {priority} {fixture_name}")
    sleep(sleep_seconds)
    print(f"OUT {priority} {fixture_name}")
    return fixture_name
