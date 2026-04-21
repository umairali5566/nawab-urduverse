#!/usr/bin/env python
"""
Test script to check poetry data and test encoding fixes
"""

import os
import django
from poetry.models import Poetry

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nawab_urduverse.settings')
django.setup()

def test_encoding_fix():
    """Test the encoding fix function with sample corrupted text."""
    poem = Poetry()

    # Test with corrupted Urdu text (this is how it appears when double-encoded)
    corrupted_title = "Ã˜Â§Ã˜Â²Ã™â€žÃ˜Â§Ã™â€"
    corrupted_content = "Ã˜Â§Ã˜Â²Ã™â€žÃ˜Â§Ã™â€ Ã™â€ Ã˜Â§Ã˜Â²Ã™â€žÃ˜Â§Ã™â€"

    print("Testing encoding detection and fixing...")

    # Print safely to avoid encoding issues
    try:
        print(f"Corrupted title: {repr(corrupted_title)}")
    except Exception:
        print("Corrupted title: [encoding issue]")

    print(f"Is corrupted: {poem._is_corrupted_utf8(corrupted_title)}")

    if poem._is_corrupted_utf8(corrupted_title):
        fixed_title = poem._fix_encoding(corrupted_title)
        try:
            print(f"Fixed title: {repr(fixed_title)}")
        except Exception:
            print("Fixed title: [encoding issue]")

    try:
        print(f"Corrupted content: {repr(corrupted_content)}")
    except Exception:
        print("Corrupted content: [encoding issue]")

    print(f"Is corrupted: {poem._is_corrupted_utf8(corrupted_content)}")

    if poem._is_corrupted_utf8(corrupted_content):
        fixed_content = poem._fix_encoding(corrupted_content)
        try:
            print(f"Fixed content: {repr(fixed_content)}")
        except Exception:
            print("Fixed content: [encoding issue]")

    # Test with actual Urdu text to see if it gets detected as corrupted
    try:
        urdu_text = "ازلان"
        print(f"\nTesting with Urdu text: {repr(urdu_text)}")
        print(f"Is Urdu text corrupted: {poem._is_corrupted_utf8(urdu_text)}")
    except Exception:
        print("Urdu text test failed due to encoding")

def check_poetry_data():
    """Check existing poetry data."""
    poems = Poetry.objects.all()
    print(f"\nTotal poetry records: {poems.count()}")

    for poem in poems[:3]:  # Check first 3 poems
        print(f"\nPoem ID: {poem.id}")
        try:
            print(f"Title: {repr(poem.title)}")
        except Exception:
            print("Title: [encoding issue]")
        try:
            content_preview = poem.content[:100] if poem.content else 'None'
            print(f"Content preview: {repr(content_preview)}")
        except Exception:
            print("Content preview: [encoding issue]")
        print(f"Title corrupted: {poem._is_corrupted_utf8(poem.title)}")
        print(f"Content corrupted: {poem._is_corrupted_utf8(poem.content)}")

if __name__ == '__main__':
    test_encoding_fix()
    check_poetry_data()