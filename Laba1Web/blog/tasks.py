import websockets

import json
from datetime import datetime
from time import sleep

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from celery import shared_task, Task, task

from Laba1Web.celery import app  # app is your celery application
from Laba1Web.settings import EMAIL_HOST_USER
from . import models as M

hostname = "127.0.0.1:8000"


# celery -A  Laba1Web worker -n A -l INFO --concurrency 1 -P solo -Q big_tasks
# celery -A  Laba1Web worker -n B -l INFO --concurrency 1 -P solo -Q messages
# celery -A Laba1Web flower
async def websocket_task_callback(message):
    data = {'type': 'task_callback',
            'message': message,
            'time': datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
    try:
        path = "ws://%s/callbacks/" % hostname
        async with websockets.connect(path) as websocket:
            await websocket.send(json.dumps(data))
    except ConnectionRefusedError:
        pass
    except Exception as exc:
        raise


class CallbackTask(Task):
    name = 'callbacktask'

    def run(self, *args, **kwargs):
        pass

    def on_success(self, retval, task_id, args, kwargs):
        message = "Task <b>%s</b>:%s finished with result %s; Args: %s; Kwargs: %s" % (self.name, task_id,
                                                                                str(retval), str(args), str(kwargs))
        async_to_sync(websocket_task_callback)(message)
        print("TaskID= %s, Result is %s" % (task_id, retval))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        pass


@shared_task(name="comments_cleanup", base=CallbackTask)
def comments_cleanup():
    counter = 0
    recipients = dict()
    try:
        comments = M.Comment.objects.all()
        with open("blog/censored.json") as list_file: # censored words contained in list in file
            censored_words = json.load(list_file)
        for c in comments:
            txt = c.text.lower()  # not calling lower for every word
            for word in censored_words:
                if word in txt:     # minimal check
                    recipients.setdefault(c.user.id, set()).add(c.post.id)
                    counter += 1
                    c.delete()
                    break
        if counter > 0:
            for key, set_val in recipients.items():
                recipients[key] = list(set_val)     # transform set into list for serialization
            send_warning.delay(recipients)
        # sleep(1) # too fast when called from page
        return counter
    except Exception as exc:
        raise


@shared_task(name="send_warning", ignore_result=True, base=CallbackTask)
def send_warning(recipients):

    for uid, pids in recipients.items():
        try:
            user = get_user_model().objects.get(pk=uid)
            poststr = ""
            for id in pids:
                poststr += "<a href=http://%s/post/%d>#%d</a>, " % (hostname, id, id)
            send_mail(
                'Blog warning',
                'Dear user %s.\n ' % user.username,
                EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
                html_message='<p>Your comments on posts %s was removed due to our censorship policy. Beware of ban <p>' % poststr
            )
        except get_user_model().DoesNotExist:
            print("User does not exist")
            pass
        except Exception as exc:
            raise
