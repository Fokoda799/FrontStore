import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frontstore.settings.dev")

celery = Celery("frontstore")
celery.config_from_object("django.conf:settings", namespace="CELERY")
celery.autodiscover_tasks()

celery.conf.timezone = "Africa/Casablanca"
celery.conf.enable_utc = True
