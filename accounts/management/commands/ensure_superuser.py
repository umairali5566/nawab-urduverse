import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update the deployment superuser from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()

        missing = [
            env_name
            for env_name, value in (
                ("DJANGO_SUPERUSER_USERNAME", username),
                ("DJANGO_SUPERUSER_PASSWORD", password),
                ("DJANGO_SUPERUSER_EMAIL", email),
            )
            if not value
        ]
        if missing:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping superuser setup because these environment variables are missing: "
                    + ", ".join(missing)
                )
            )
            return

        User = get_user_model()
        username_field = User.USERNAME_FIELD
        email_field = User.get_email_field_name()
        manager = User._default_manager

        lookup = {username_field: username}
        user = manager.filter(**lookup).first()

        if user is None:
            manager.create_superuser(
                **{
                    username_field: username,
                    email_field: email,
                    "password": password,
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Created deployment superuser '{username}'"))
            return

        updated = False
        if getattr(user, email_field, "") != email:
            setattr(user, email_field, email)
            updated = True

        if not user.is_staff:
            user.is_staff = True
            updated = True

        if not user.is_superuser:
            user.is_superuser = True
            updated = True

        if hasattr(user, "is_active") and not user.is_active:
            user.is_active = True
            updated = True

        if not user.check_password(password):
            user.set_password(password)
            updated = True

        if updated:
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated deployment superuser '{username}'"))
            return

        self.stdout.write(self.style.SUCCESS(f"Deployment superuser '{username}' already exists"))
