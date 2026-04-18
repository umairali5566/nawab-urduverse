from django.core.management.base import BaseCommand

from accounts.deployment import ensure_deployment_superuser


class Command(BaseCommand):
    help = "Create or update the deployment superuser from environment variables."

    def handle(self, *args, **options):
        success, status = ensure_deployment_superuser()
        if not success and status == "missing_env":
            self.stdout.write(
                self.style.WARNING(
                    "Skipping superuser setup because DJANGO_SUPERUSER_USERNAME, "
                    "DJANGO_SUPERUSER_PASSWORD, or DJANGO_SUPERUSER_EMAIL is missing."
                )
            )
            return

        messages = {
            "created": self.style.SUCCESS("Created deployment superuser from environment variables."),
            "updated": self.style.SUCCESS("Updated deployment superuser from environment variables."),
            "unchanged": self.style.SUCCESS("Deployment superuser already exists and is up to date."),
        }
        self.stdout.write(messages.get(status, self.style.SUCCESS("Deployment superuser ensured.")))
