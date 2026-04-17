from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands.createsuperuser import Command as DjangoCreateSuperuserCommand
from django.core.management.base import CommandError
from django.db import IntegrityError


class Command(DjangoCreateSuperuserCommand):
    help = "Create a superuser with clearer validation for duplicate email addresses."

    def handle(self, *args, **options):
        try:
            return super().handle(*args, **options)
        except IntegrityError as exc:
            message = str(exc)
            if "accounts_user.email" not in message:
                raise

            email = options.get(self.UserModel.get_email_field_name())
            extra = ""
            if email:
                existing_user = get_user_model()._default_manager.filter(email=email).first()
                if existing_user:
                    role = "superuser" if existing_user.is_superuser else "user"
                    extra = (
                        f" Existing account: username='{existing_user.get_username()}', role='{role}'."
                    )

            raise CommandError(
                "A user with this email address already exists."
                f"{extra} Use a different email, or update the existing account instead."
            ) from exc
