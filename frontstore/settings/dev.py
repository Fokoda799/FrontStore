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

CELERY_BROKER_URL = "redis://localhost:6379/1"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
