import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates a superuser from environment variables if one doesn't exist"

    def handle(self, *args, **options):
        User = get_user_model()

        # Read credentials from environment variables so they never
        # appear hardcoded in your source code
        username = os.environ.get("DJANGO_ADMIN_USERNAME", "admin")
        email = os.environ.get("DJANGO_ADMIN_EMAIL", "admin@example.com")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_ADMIN_PASSWORD not set — skipping admin creation."
                )
            )
            return

        # Only create the admin if it doesn't already exist,
        # so re-running this on every deploy is completely safe
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' created successfully.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' already exists — skipping.")
            )
