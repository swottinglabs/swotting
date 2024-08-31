from huey import crontab
from huey.contrib.djhuey import periodic_task, task

@task()
def my_background_task(param):
    # Your task logic here
    pass

@periodic_task(crontab(minute='0', hour='*/3'))
def my_periodic_task():
    # Your periodic task logic here
    pass
