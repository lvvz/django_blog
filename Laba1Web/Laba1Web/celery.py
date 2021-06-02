import os
import json

from celery import Celery
from kombu import Queue, Exchange

# set the default Django settings module for the 'celery' program.
# this is also used in manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Laba1Web.settings')
app = Celery('Laba1Web')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.task_create_missing_queues = True
app.autodiscover_tasks()

with open("Laba1Web/db_setting.json") as db_file:
    conf = json.load(db_file)
    app.conf.broker_url = conf["broker_url"]
    app.conf.result_backend = conf["result_back"]

app.conf.beat_schedule = {
    'scheduled_comment_cleanup': {
        'task': 'comments_cleanup',
        'schedule': 120.0,
    },
}

app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('messages', Exchange('messages'), routing_key='messages'),
    Queue('big_tasks', Exchange('big_tasks'), routing_key='big_tasks'),
)

app.conf.task_routes = {
    'comments_cleanup': {'queue': 'big_tasks', 'routing_key': 'big_tasks'},
    'send_warning': {'queue': 'messages', 'routing_key': 'messages'},
}


