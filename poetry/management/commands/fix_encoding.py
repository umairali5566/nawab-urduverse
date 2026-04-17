"""
Django management command to fix UTF-8 encoding issues in Poetry model.
Fixes double-encoded Urdu text that appears as "Ã˜Â§Ã˜Â²Ã™â€žÃ˜Â§Ã™â€".
"""

import re
from django.core.management.base import BaseCommand
from poetry.models import Poetry


class Command(BaseCommand):
    help = 'Fix UTF-8 encoding issues in Poetry model records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE: No changes will be made')
            )

        # Pattern to detect double-encoded UTF-8 (Latin-1 interpreted as UTF-8)
        # This matches sequences like Ã˜Â§Ã˜Â²Ã™â€žÃ˜Â§Ã™â€
        corrupted_pattern = re.compile(r'[Ã][^\x00-\x7F]{1,4}')

        def is_corrupted(text):
            """Check if text contains corrupted UTF-8 sequences."""
            return bool(corrupted_pattern.search(text or ''))

        def fix_encoding(text):
            """Fix double-encoded UTF-8 text."""
            if not text:
                return text
            try:
                # Decode from latin1 (which was misinterpreted as utf-8) back to bytes,
                # then decode as proper utf-8
                return text.encode('latin1').decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError):
                # If fixing fails, return original text
                return text

        # Process all Poetry records
        poems = Poetry.objects.all()
        total_poems = poems.count()
        fixed_count = 0

        self.stdout.write(f'Processing {total_poems} poetry records...')

        for poem in poems:
            title_fixed = False
            content_fixed = False

            # Check and fix title
            if is_corrupted(poem.title):
                old_title = poem.title
                new_title = fix_encoding(poem.title)
                if not dry_run:
                    poem.title = new_title
                title_fixed = True
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f'[DRY RUN] Would fix title: "{old_title}" -> "{new_title}"')
                    )

            # Check and fix content
            if is_corrupted(poem.content):
                old_content = poem.content[:100] + '...' if len(poem.content) > 100 else poem.content
                new_content = fix_encoding(poem.content)
                if not dry_run:
                    poem.content = new_content
                content_fixed = True
                if dry_run:
                    new_content_preview = new_content[:100] + '...' if len(new_content) > 100 else new_content
                    self.stdout.write(
                        self.style.WARNING(f'[DRY RUN] Would fix content: "{old_content}" -> "{new_content_preview}"')
                    )

            if title_fixed or content_fixed:
                fixed_count += 1
                if not dry_run:
                    poem.save(update_fields=['title', 'content'] if title_fixed and content_fixed
                             else ['title'] if title_fixed else ['content'])
                    self.stdout.write(
                        self.style.SUCCESS(f'Fixed poetry "{poem.title}" (ID: {poem.id})')
                    )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY RUN: Would fix {fixed_count} out of {total_poems} records')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully fixed {fixed_count} out of {total_poems} records')
            )

        if fixed_count == 0:
            self.stdout.write(
                self.style.SUCCESS('No corrupted text found - all records appear to be properly encoded')
            )