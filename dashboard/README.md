# Nawab Urdu Academy - Admin Dashboard

A comprehensive content management system for Urdu literature platform.

## Features

### Content Management
- **Poetry**: Add, edit, and manage Urdu poetry with author attribution
- **Novels**: Manage novels with chapters, reviews, and reading progress
- **Stories**: Short stories with categories and metadata
- **Blog Posts**: Blog content with rich text and featured images
- **Quotes**: Inspirational quotes with customizable styling
- **Videos**: Video content with multiple platform support

### Bulk Upload
- CSV-based bulk upload for all content types
- Automatic author and category creation
- Input validation and error handling
- Progress tracking and success reporting

### Admin Interface
- Professional, responsive dashboard design
- Real-time statistics and analytics
- User management and activity monitoring
- Content moderation tools
- SEO and metadata management

### Security Features
- Role-based access control
- File upload validation
- CSRF protection
- Input sanitization
- Secure authentication

## Installation

1. Ensure Django admin is configured
2. Add dashboard URLs to main URLconf
3. Run migrations
4. Create superuser account

## Usage

### Adding Content

1. **Individual Content**: Use the "Add [Content Type]" buttons in the dashboard
2. **Bulk Upload**: Upload CSV files with proper formatting

### CSV Format Examples

#### Poetry
```csv
title,author,content
شعر کا عنوان,شاعر کا نام,شعر کی کامل متن
```

#### Quotes
```csv
text,author,quote_type
اقتباس کی متن,مصنف کا نام,motivational
```

#### Stories
```csv
title,author,content
کہانی کا عنوان,مصنف کا نام,کہانی کی مکمل متن
```

### Permissions

- **Superuser**: Full access to all features
- **Staff**: Limited content management access

## API Reference

### Views

- `dashboard_home`: Main dashboard with statistics
- `bulk_upload`: CSV file processing endpoint
- `add_[content_type]`: Individual content creation forms

### Models

All content models inherit from base classes with common fields:
- `title`, `slug`, `author`, `is_published`
- `created_at`, `updated_at`, `views_count`

## Performance Optimizations

- Database query optimization with `select_related`
- Efficient pagination (12 items per page)
- View count caching
- Lazy loading of related objects

## Security Measures

- File type and size validation
- HTML tag stripping from user input
- CSRF token validation
- User permission checks
- Secure file handling

## Contributing

1. Follow Django best practices
2. Add proper docstrings
3. Include unit tests
4. Update documentation