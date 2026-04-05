from django.core.management.base import BaseCommand, CommandError

from core.redis_health import check_redis_connection


class Command(BaseCommand):
    help = "Check Redis connectivity using REDIS_URL or cache LOCATION."

    def handle(self, *args, **options):
        result = check_redis_connection()
        if result.get("ok"):
            url = result.get("url", "")
            self.stdout.write(self.style.SUCCESS(f"Redis OK: {url}"))
            return

        error = result.get("error", "Unknown error")
        url = result.get("url", "unknown")
        raise CommandError(f"Redis check failed: {error} (url={url})")
