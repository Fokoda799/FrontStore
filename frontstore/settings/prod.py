import os
import ssl

import dj_database_url

from .common import *  # noqa: F401, F403

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")
DATABASES = {"default": dj_database_url.config()}

REDIS_URL = os.environ["REDIS_URL"]

CELERY_BROKER_URL = "rediss://default:nVqgWiHe40XLgUITWQzC4DuBw6u4quHj@redis-16942.c44.us-east-1-2.ec2.cloud.redislabs.com:16942"  # noqa: E501
CELERY_RESULT_BACKEND = "rediss://default:nVqgWiHe40XLgUITWQzC4DuBw6u4quHj@redis-16942.c44.us-east-1-2.ec2.cloud.redislabs.com:16942"  # noqa: E501
# Required for Redis Cloud SSL
CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE}

CELERY_RESULT_BACKEND_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "rediss://default:nVqgWiHe40XLgUITWQzC4DuBw6u4quHj@redis-16942.c44.us-east-1-2.ec2.cloud.redislabs.com:16942",  # noqa: E501
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"ssl_cert_reqs": None},
        },
    }
}
