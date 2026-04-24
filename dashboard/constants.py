"""
Dashboard Constants and Utilities
"""

# Content type mappings for bulk upload
CONTENT_TYPES = {
    'poetry': {
        'model': 'poetry.Poetry',
        'required_fields': ['title', 'content'],
        'optional_fields': ['author'],
    },
    'quotes': {
        'model': 'quotes.Quote',
        'required_fields': ['text'],
        'optional_fields': ['author', 'quote_type'],
    },
    'stories': {
        'model': 'stories.Story',
        'required_fields': ['title', 'author', 'content'],
        'optional_fields': [],
    },
    'blog': {
        'model': 'blog.BlogPost',
        'required_fields': ['title', 'content'],
        'optional_fields': ['author'],
    },
    'novels': {
        'model': 'novels.Novel',
        'required_fields': ['title', 'content'],
        'optional_fields': ['author'],
    },
    'videos': {
        'model': 'videos.Video',
        'required_fields': ['title', 'video_url'],
        'optional_fields': ['author', 'video_type', 'description'],
    },
}

# File upload settings
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = ['.csv']

# Validation messages
VALIDATION_MESSAGES = {
    'missing_fields': 'Please select a content type and upload a CSV file.',
    'invalid_file_type': 'Only CSV files are allowed.',
    'file_too_large': 'File size must be less than 5MB.',
    'processing_error': 'Error processing file: {}',
    'success': 'Successfully created {} items.',
}
