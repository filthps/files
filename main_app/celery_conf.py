import os
from django.conf import settings
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'files.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')


app = Celery('main_app')
app.config_from_object('django.conf:settings')


app.autodiscover_tasks(settings.INSTALLED_APPS)
