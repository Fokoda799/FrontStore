import os
import ssl

import dj_database_url

from .common import *  # noqa: F401, F403

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")
DATABASES = {"default": dj_database_url.config()}

REDIS_URL = os.environ["REDIS_URL"]

CELERY_BROKER_URL = REDIS_URL
CELERY_BROKER_USE_SSL = {
    "ssl_ca_certs": "/redis_ca.pem",
    "ssl_cert_reqs": ssl.CERT_REQUIRED,
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"ssl_cert_reqs": None},
        },
    }
}
