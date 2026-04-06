from .common import *  # noqa: F403

DEBUG = True

SECRET_KEY = "django-insecure-r-n#9jk6j(i3ot0v-mj*49_sikp6mn-(q+p_2u$(9$8l(kd9sy"

INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405

MIDDLEWARE += [  # noqa: F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "silk.middleware.SilkyMiddleware",
]

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

REDIS_URL = "redis://localhost:6379/0"

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = "django-db"  # store results in your local DB

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
