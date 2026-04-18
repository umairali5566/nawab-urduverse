import logging
import os

from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)


def ensure_deployment_superuser():
    """
    Create or update the deployment superuser from environment variables.

    Safe to call repeatedly from post_migrate or startup commands.
    """
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
        logger.info(
            "Skipping deployment superuser setup because these environment variables are missing: %s",
            ", ".join(missing),
        )
        return False, "missing_env"

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
        logger.info("Created deployment superuser '%s'", username)
        return True, "created"

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
        logger.info("Updated deployment superuser '%s'", username)
        return True, "updated"

    logger.info("Deployment superuser '%s' already exists", username)
    return True, "unchanged"
