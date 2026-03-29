import os

from .common import *  # noqa: F403

DEBUG = True

SECRET_KEY = "django-insecure-r-n#9jk6j(i3ot0v-mj*49_sikp6mn-(q+p_2u$(9$8l(kd9sy"

MIDDLEWARE += ["silk.middleware.SilkyMiddleware"]  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "frontstore",
        "HOST": "localhost",
        "USER": "root",
        "PASSWORD": "wac2003A",
        # 'CONN_MAX_AGE': 60
    }
}

REDIS_URL = os.environ["REDIS_URL"]

CELERY_BROKER_URL = REDIS_URL

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
