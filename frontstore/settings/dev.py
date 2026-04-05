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

CELERY_BROKER_URL = "redis://default:nVqgWiHe40XLgUITWQzC4DuBw6u4quHj@redis-16942.c44.us-east-1-2.ec2.cloud.redislabs.com:16942"  # noqa: E501

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://default:nVqgWiHe40XLgUITWQzC4DuBw6u4quHj@redis-16942.c44.us-east-1-2.ec2.cloud.redislabs.com:16942",  # noqa: E501
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
