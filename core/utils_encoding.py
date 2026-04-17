"""
Urdu Text Encoding Utilities for Nawab Urdu Academy
Provides functions to fix corrupted UTF-8 text and clean HTML tags
"""

import re
from html import unescape


def repair_double_encoded_text(text):
    """
    Fix double-encoded Urdu text.
    
    Issue: When UTF-8 text is treated as Latin-1 and re-encoded as UTF-8,
    it becomes corrupted like "Ø§ÙØ±Ø²Ùˆ" instead of "آرزو"
    
    Fix: Encode as Latin-1 then decode as UTF-8 to reverse the double encoding.
    
    Args:
        text (str): Potentially corrupted text
        
    Returns:
        str: Fixed UTF-8 text
    """
    if not text:
        return text
    
    try:
        fixed = text.encode('latin1').decode('utf-8')
        return fixed
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        return text


def is_likely_corrupted(text):
    """
    Check if text shows signs of double encoding.
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if text appears to be double-encoded
    """
    if not text:
        return False
    
    corrupted_patterns = ['Ø', '§', 'Ù', '±', '²', 'ˆ']
    return any(char in text for char in corrupted_patterns)


def clean_html_tags(text, preserve_breaks=True):
    """
    Clean HTML tags from text while preserving Urdu text formatting.
    
    Args:
        text (str): HTML text to clean
        preserve_breaks (bool): Whether to preserve line breaks
        
    Returns:
        str: Clean text with HTML removed
    """
    if not text:
        return text
    
    result = text
    
    if preserve_breaks:
        result = re.sub(r'<\s*br\s*/?\s*>', '\n', result, flags=re.IGNORECASE)
        result = re.sub(r'</p\s*>', '\n', result, flags=re.IGNORECASE)
        result = re.sub(r'<\s*p[^>]*>', '\n', result, flags=re.IGNORECASE)
    
    result = re.sub(r'<[^>]+>', '', result)
    result = unescape(result)
    
    lines = [line.strip() for line in result.splitlines() if line.strip()]
    return '\n'.join(lines)


def normalize_poetry_text(text):
    """
    Normalize poetry text to plain format.
    
    Args:
        text (str): Poetry text with HTML formatting
        
    Returns:
        str: Clean poetry text with lines separated by newlines
    """
    return clean_html_tags(text, preserve_breaks=True)


def fix_model_field_encoding(obj, field_names):
    """
    Fix encoding issues in multiple model fields.
    
    Args:
        obj: Django model instance
        field_names (list): List of field names to check and fix
        
    Returns:
        tuple: (fixed_count, any_changes)
    """
    fixed_count = 0
    any_changes = False
    
    for field_name in field_names:
        if not hasattr(obj, field_name):
            continue
            
        value = getattr(obj, field_name)
        if not value or not isinstance(value, str):
            continue
            
        if is_likely_corrupted(value):
            fixed = repair_double_encoded_text(value)
            if fixed != value:
                setattr(obj, field_name, fixed)
                fixed_count += 1
                any_changes = True
    
    return fixed_count, any_changes


def repair_all_poetry_content():
    """
    Repair all corrupted poetry content in the database.
    
    Run this in Django shell to fix existing corrupted data:
    >>> from core.utils_encoding import repair_all_poetry_content
    >>> repair_all_poetry_content()
    
    Returns:
        dict: Repair statistics
    """
    from poetry.models import Poetry
    from core.models import Content
    
    stats = {
        'poetry_checked': 0,
        'poetry_fixed': 0,
        'content_checked': 0,
        'content_fixed': 0,
    }
    
    for poem in Poetry.objects.all():
        stats['poetry_checked'] += 1
        fixed_count, changed = fix_model_field_encoding(
            poem, 
            ['title', 'content', 'meta_title', 'meta_description']
        )
        if changed:
            poem.save(update_fields=['title', 'content', 'meta_title', 'meta_description'])
            stats['poetry_fixed'] += 1
    
    for content in Content.objects.all():
        stats['content_checked'] += 1
        fixed_count, changed = fix_model_field_encoding(
            content,
            ['title', 'text']
        )
        if changed:
            content.save(update_fields=['title', 'text'])
            stats['content_fixed'] += 1
    
    return stats


def fix_author_names():
    """
    Repair all corrupted author names.
    
    Returns:
        dict: Repair statistics
    """
    from core.models import Author
    
    stats = {'checked': 0, 'fixed': 0}
    
    for author in Author.objects.all():
        stats['checked'] += 1
        if is_likely_corrupted(author.name):
            author.name = repair_double_encoded_text(author.name)
            author.save(update_fields=['name'])
            stats['fixed'] += 1
    
    return stats


def fix_category_names():
    """
    Repair all corrupted category names.
    
    Returns:
        dict: Repair statistics
    """
    from core.models import Category
    
    stats = {'checked': 0, 'fixed': 0}
    
    for category in Category.objects.all():
        stats['checked'] += 1
        changed = False
        
        if is_likely_corrupted(category.name):
            category.name = repair_double_encoded_text(category.name)
            changed = True
            
        if category.description and is_likely_corrupted(category.description):
            category.description = repair_double_encoded_text(category.description)
            changed = True
            
        if changed:
            category.save()
            stats['fixed'] += 1
    
    return stats


def fix_novels_and_chapters():
    """
    Repair all corrupted novel and chapter content.
    
    Returns:
        dict: Repair statistics
    """
    from novels.models import Novel, Chapter
    
    stats = {
        'novels_checked': 0,
        'novels_fixed': 0,
        'chapters_checked': 0,
        'chapters_fixed': 0,
    }
    
    for novel in Novel.objects.all():
        stats['novels_checked'] += 1
        changed = False
        
        if is_likely_corrupted(novel.title):
            novel.title = repair_double_encoded_text(novel.title)
            changed = True
        
        if novel.description and is_likely_corrupted(novel.description):
            novel.description = repair_double_encoded_text(novel.description)
            changed = True
        
        if novel.meta_title and is_likely_corrupted(novel.meta_title):
            novel.meta_title = repair_double_encoded_text(novel.meta_title)
            changed = True
        
        if novel.meta_description and is_likely_corrupted(novel.meta_description):
            novel.meta_description = repair_double_encoded_text(novel.meta_description)
            changed = True
        
        if changed:
            novel.save(update_fields=['title', 'description', 'meta_title', 'meta_description'])
            stats['novels_fixed'] += 1
    
    for chapter in Chapter.objects.all():
        stats['chapters_checked'] += 1
        changed = False
        
        if is_likely_corrupted(chapter.title):
            chapter.title = repair_double_encoded_text(chapter.title)
            changed = True
        
        if chapter.content and is_likely_corrupted(chapter.content):
            chapter.content = repair_double_encoded_text(chapter.content)
            changed = True
        
        if chapter.meta_title and is_likely_corrupted(chapter.meta_title):
            chapter.meta_title = repair_double_encoded_text(chapter.meta_title)
            changed = True
        
        if chapter.meta_description and is_likely_corrupted(chapter.meta_description):
            chapter.meta_description = repair_double_encoded_text(chapter.meta_description)
            changed = True
        
        if changed:
            chapter.save(update_fields=['title', 'content', 'meta_title', 'meta_description'])
            stats['chapters_fixed'] += 1
    
    return stats


def repair_all_content():
    """
    Comprehensive function to repair all corrupted content in the database.
    
    Run this in Django shell to fix all existing corrupted data:
    >>> from core.utils_encoding import repair_all_content
    >>> repair_all_content()
    
    Returns:
        dict: Repair statistics for all content types
    """
    poetry_stats = repair_all_poetry_content()
    author_stats = fix_author_names()
    category_stats = fix_category_names()
    novel_stats = fix_novels_and_chapters()
    
    return {
        'poetry': poetry_stats,
        'authors': author_stats,
        'categories': category_stats,
        'novels': novel_stats,
    }