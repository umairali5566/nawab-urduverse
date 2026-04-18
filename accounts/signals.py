from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .deployment import ensure_deployment_superuser


@receiver(post_migrate)
def create_deployment_superuser(sender, **kwargs):
    """
    Ensure the production admin user exists after migrations complete.
    """
    if getattr(sender, "name", "") != "accounts":
        return

    ensure_deployment_superuser()
