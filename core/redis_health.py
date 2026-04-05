import os
from urllib.parse import urlparse, urlunparse

import redis
from django.conf import settings


def _redact_redis_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.password:
        return url
    netloc = parsed.hostname or ""
    if parsed.username:
        netloc = f"{parsed.username}:***@{netloc}"
    else:
        netloc = f"***@{netloc}"
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    return urlunparse(parsed._replace(netloc=netloc))


def _get_redis_url() -> str | None:
    url = getattr(settings, "REDIS_URL", None) or os.environ.get("REDIS_URL")
    if url:
        return url
    caches = getattr(settings, "CACHES", {}) or {}
    default_cache = caches.get("default", {}) or {}
    location = default_cache.get("LOCATION")
    if isinstance(location, (list, tuple)):
        location = location[0] if location else None
    if isinstance(location, str) and location:
        return location
    return None


def check_redis_connection() -> dict:
    url = _get_redis_url()
    if not url:
        return {"ok": False, "error": "REDIS_URL is not configured"}

    client = None
    try:
        client = redis.from_url(url, socket_connect_timeout=2, socket_timeout=2)
        client.ping()
        return {"ok": True, "url": _redact_redis_url(url)}
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "url": _redact_redis_url(url),
            "error": str(exc),
        }
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:  # noqa: BLE001
                pass
