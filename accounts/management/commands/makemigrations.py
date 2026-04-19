"""
Block makemigrations on production (Render).
This prevents accidental schema changes in production.
"""

import os
from django.core.management.base import CommandError
from django.core.management.commands.makemigrations import Command as MakemigrationsCommand


class Command(MakemigrationsCommand):
    """Override makemigrations to prevent running on Render."""
    
    def handle(self, *app_labels, **options):
        if os.environ.get('RENDER'):
            raise CommandError(
                '❌ BLOCKED: makemigrations is not allowed on Render production.\n'
                '\n'
                'Fix:\n'
                '1. Generate migrations locally: python manage.py makemigrations\n'
                '2. Test migrations locally: python manage.py migrate\n'
                '3. Commit migrations to git\n'
                '4. Deploy to Render (migrations will run automatically)\n'
                '\n'
                'The build command runs: python manage.py migrate\n'
                'This applies pre-generated migrations safely.\n'
            )
        
        return super().handle(*app_labels, **options)
