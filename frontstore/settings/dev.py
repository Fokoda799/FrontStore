import os

from .common import *  # noqa: F403

# Load .env for local development without extra dependencies.
env_path = os.path.join(BASE_DIR, ".env")  # noqa: F405
if os.path.exists(env_path):  # noqa: F405
    with open(env_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)  # noqa: F405

DEBUG = True

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-r-n#9jk6j(i3ot0v-mj*49_sikp6mn-(q+p_2u$(9$8l(kd9sy",
)

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405

MIDDLEWARE += [  # noqa: F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "silk.middleware.SilkyMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.mysql"),
        "NAME": os.environ.get("DB_NAME", "frontstore"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "wac2003A"),
        # 'CONN_MAX_AGE': 60
    }
}

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

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

EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")  # noqa: F405
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")  # noqa: F405
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")  # noqa: F405
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "")  # noqa: F405
