"""
Safe migrate command that prevents interactive prompts on Render.
This ensures migrations run safely without user input.
"""

from django.core.management.commands.migrate import Command as MigrateCommand


class Command(MigrateCommand):
    """Override migrate command to run safely in production."""
    
    def handle(self, *args, **options):
        # Force non-interactive mode on Render
        import os
        if os.environ.get('RENDER'):
            options['interactive'] = False
        
        return super().handle(*args, **options)
