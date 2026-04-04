# Nawab UrduVerse - Project Structure

This document provides a comprehensive overview of the project structure and architecture.

## Directory Structure

```
nawab_urduverse/
│
├── nawab_urduverse/              # Main Django project configuration
│   ├── __init__.py
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Main URL configuration
│   ├── wsgi.py                   # WSGI application
│   └── asgi.py                   # ASGI application
│
├── accounts/                     # User authentication app
│   ├── __init__.py
│   ├── admin.py                  # Admin configuration
│   ├── apps.py                   # App configuration
│   ├── forms.py                  # User forms
│   ├── models.py                 # User models
│   ├── urls.py                   # URL patterns
│   └── views.py                  # View functions
│
├── core/                         # Core functionality app
│   ├── __init__.py
│   ├── admin.py                  # Admin configuration
│   ├── apps.py                   # App configuration
│   ├── context_processors.py     # Template context processors
│   ├── models.py                 # Core models (Category, Author, etc.)
│   ├── sitemaps.py               # SEO sitemaps
│   ├── urls.py                   # URL patterns
│   └── views.py                  # View functions
│
├── novels/                       # Novels app
│   ├── __init__.py
│   ├── admin.py                  # Admin configuration
│   ├── apps.py                   # App configuration
│   ├── models.py                 # Novel and Chapter models
│   ├── urls.py                   # URL patterns
│   └── views.py                  # View functions
│
├── stories/                      # Stories app
│   ├── __init__.py
│   ├── admin.py                  # Admin configuration
│   ├── apps.py                   # App configuration
│   ├── models.py                 # Story model
│   ├── urls.py                   # URL patterns
│   └── views.py                  # View functions
│
├── poetry/                       # Poetry app
│   ├── __init__.py
│   ├── admin.py                  # Admin configuration
│   ├── apps.py                   # App configuration
│   ├── models.py                 # Poetry and Collection models
│   ├── urls.py                   # URL patterns
│   └── views.py                  # View functions
│
├── quotes/                       # Quotes app
│   ├── __init__.py
│   ├── admin.py                  # Admin configuration
│   ├── apps.py                   # App configuration
│   ├── models.py                 # Quote and Collection models
│   ├── urls.py                   # URL patterns
│   └── views.py                  # View functions
│
├── blog/                         # Blog app
│   ├── __init__.py
│   ├── admin.py                  # Admin configuration
│   ├── apps.py                   # App configuration
│   ├── models.py                 # BlogPost model
│   ├── urls.py                   # URL patterns
│   └── views.py                  # View functions
│
├── videos/                       # Videos app
│   ├── __init__.py
│   ├── admin.py                  # Admin configuration
│   ├── apps.py                   # App configuration
│   ├── models.py                 # Video and Playlist models
│   ├── urls.py                   # URL patterns
│   └── views.py                  # View functions
│
├── templates/                    # HTML templates
│   ├── base.html                 # Base template
│   ├── core/                     # Core templates
│   │   ├── home.html
│   │   ├── about.html
│   │   ├── contact.html
│   │   ├── author_list.html
│   │   ├── author_detail.html
│   │   ├── search.html
│   │   ├── category_detail.html
│   │   ├── privacy_policy.html
│   │   └── terms_of_service.html
│   ├── accounts/                 # Account templates
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   ├── edit_profile.html
│   │   ├── change_password.html
│   │   ├── bookmarks.html
│   │   └── delete_account.html
│   ├── novels/                   # Novel templates
│   │   ├── novel_list.html
│   │   ├── novel_detail.html
│   │   ├── chapter_detail.html
│   │   └── categories.html
│   ├── stories/                  # Story templates
│   │   ├── story_list.html
│   │   ├── story_detail.html
│   │   └── categories.html
│   ├── poetry/                   # Poetry templates
│   │   ├── poetry_list.html
│   │   ├── poetry_detail.html
│   │   ├── collection_list.html
│   │   ├── collection_detail.html
│   │   ├── poetry_by_type.html
│   │   └── poetry_by_mood.html
│   ├── quotes/                   # Quote templates
│   │   ├── quote_list.html
│   │   ├── quote_detail.html
│   │   ├── collection_list.html
│   │   ├── collection_detail.html
│   │   └── quotes_by_type.html
│   ├── blog/                     # Blog templates
│   │   ├── blog_list.html
│   │   └── blog_detail.html
│   ├── videos/                   # Video templates
│   │   ├── video_list.html
│   │   ├── video_detail.html
│   │   ├── playlist_list.html
│   │   ├── playlist_detail.html
│   │   └── videos_by_type.html
│   └── includes/                 # Reusable includes
│       ├── header.html
│       ├── footer.html
│       ├── pagination.html
│       ├── comments.html
│       └── sidebar.html
│
├── static/                       # Static files
│   ├── css/
│   │   ├── style.css             # Main stylesheet
│   │   └── dark-mode.css         # Dark mode styles
│   ├── js/
│   │   └── main.js               # Main JavaScript
│   └── images/
│       ├── favicon.ico
│       ├── logo.png
│       ├── hero-image.png
│       ├── default-novel.jpg
│       ├── default-author.jpg
│       ├── default-video.jpg
│       └── og-image.jpg
│
├── media/                        # User uploaded files (created at runtime)
│   ├── novels/
│   ├── stories/
│   ├── poetry/
│   ├── quotes/
│   ├── videos/
│   ├── authors/
│   ├── avatars/
│   └── blog/
│
├── locale/                       # Translation files
│   └── ur/
│       └── LC_MESSAGES/
│           └── django.po
│
├── logs/                         # Application logs
│
├── manage.py                     # Django management script
├── setup.py                      # Setup automation script
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── DEPLOYMENT.md                 # Deployment guide
└── PROJECT_STRUCTURE.md          # This file
```

## App Descriptions

### 1. Core App (`core/`)
**Purpose**: Foundation app containing shared functionality

**Models**:
- `Category`: Content categorization
- `Tag`: Content tagging
- `Author`: Writer/poet profiles
- `Comment`: User comments on content
- `Bookmark`: User bookmarks
- `ReadingProgress`: Track novel reading progress
- `SiteSetting`: Dynamic site configuration
- `NewsletterSubscriber`: Email subscribers
- `ContactMessage`: Contact form messages

**Key Features**:
- Global search functionality
- Author profiles
- Category browsing
- Newsletter subscription
- Contact form

### 2. Accounts App (`accounts/`)
**Purpose**: User authentication and profile management

**Models**:
- `User`: Custom user model with extended fields
- `UserActivity`: Track user activities

**Key Features**:
- User registration/login
- Profile management
- Password change
- User bookmarks
- Activity tracking

### 3. Novels App (`novels/`)
**Purpose**: Novel and chapter management

**Models**:
- `Novel`: Novel content
- `Chapter`: Novel chapters
- `NovelReview`: User reviews and ratings

**Key Features**:
- Chapter-based reading
- Reading progress tracking
- Novel reviews
- Category filtering
- Continue reading

### 4. Stories App (`stories/`)
**Purpose**: Short story management

**Models**:
- `Story`: Short story content

**Key Features**:
- Story browsing
- Category filtering
- Reading time estimation
- Comments

### 5. Poetry App (`poetry/`)
**Purpose**: Poetry content management

**Models**:
- `Poetry`: Poems and ghazals
- `PoetryCollection`: Poetry collections/diwans

**Key Features**:
- Poetry types (Ghazal, Nazm, etc.)
- Mood-based filtering
- Poetry collections
- Author collections

### 6. Quotes App (`quotes/`)
**Purpose**: Quote management with image generation

**Models**:
- `Quote`: Urdu quotes
- `QuoteCollection`: Quote collections

**Key Features**:
- Quote types (Islamic, Motivational, etc.)
- Customizable backgrounds
- Social sharing
- Image download

### 7. Blog App (`blog/`)
**Purpose**: Blog article management

**Models**:
- `BlogPost`: Blog articles
- `BlogCategory`: Blog-specific categories

**Key Features**:
- SEO-optimized posts
- Categories and tags
- Related posts
- Reading time

### 8. Videos App (`videos/`)
**Purpose**: Video content management

**Models**:
- `Video`: Embedded videos
- `VideoPlaylist`: Video playlists

**Key Features**:
- YouTube embedding
- Video playlists
- Category filtering
- Thumbnail generation

## URL Structure

```
/                           # Home page
/about/                     # About page
/contact/                   # Contact page
/search/                    # Global search
/sitemap.xml                # XML sitemap

/accounts/
    register/               # User registration
    login/                  # User login
    logout/                 # User logout
    profile/                # User profile
    profile/edit/           # Edit profile
    profile/change-password/# Change password
    profile/bookmarks/      # User bookmarks

/novels/
    /                       # Novel list
    categories/             # Novel categories
    <slug>/                 # Novel detail
    <novel>/<chapter>/      # Chapter detail

/stories/
    /                       # Story list
    categories/             # Story categories
    <slug>/                 # Story detail

/poetry/
    /                       # Poetry list
    type/<type>/            # Poetry by type
    mood/<mood>/            # Poetry by mood
    collections/            # Poetry collections
    collections/<slug>/     # Collection detail
    <slug>/                 # Poetry detail

/quotes/
    /                       # Quote list
    type/<type>/            # Quotes by type
    collections/            # Quote collections
    collections/<slug>/     # Collection detail
    <slug>/                 # Quote detail

/blog/
    /                       # Blog list
    <slug>/                 # Blog post detail

/videos/
    /                       # Video list
    type/<type>/            # Videos by type
    playlists/              # Playlists
    playlists/<slug>/       # Playlist detail
    <slug>/                 # Video detail

/authors/
    /                       # Author list
    <slug>/                 # Author detail

/category/<slug>/           # Category detail
```

## Database Schema

### Entity Relationships

```
User
├── Bookmark (M:N with content)
├── Comment (1:N)
├── ReadingProgress (1:N with Novel)
└── UserActivity (1:N)

Author
├── Novel (1:N)
├── Story (1:N)
├── Poetry (1:N)
├── Quote (1:N)
├── BlogPost (1:N)
└── Video (1:N)

Category
├── Novel (M:N)
├── Story (M:N)
├── Poetry (M:N)
├── Quote (M:N)
├── BlogPost (M:N)
└── Video (M:N)

Novel
├── Chapter (1:N)
├── NovelReview (1:N)
└── ReadingProgress (1:N)
```

## Security Considerations

1. **CSRF Protection**: Enabled on all forms
2. **SQL Injection Prevention**: Using Django ORM
3. **XSS Protection**: Template auto-escaping
4. **Clickjacking Protection**: X-Frame-Options header
5. **Secure Cookies**: HttpOnly and Secure flags in production

## Performance Optimizations

1. **Database Indexing**: Key fields indexed
2. **Query Optimization**: select_related and prefetch_related
3. **Caching**: Redis caching configured
4. **Static Files**: Whitenoise for serving
5. **CDN Ready**: Static files can be moved to CDN

## Scalability Features

1. **Modular Architecture**: Easy to extend
2. **Database Sharding Ready**: Can be configured
3. **Load Balancing**: Stateless design
4. **Caching Layers**: Multi-level caching
5. **Async Tasks**: Celery ready for background tasks

---

For more information, see README.md and DEPLOYMENT.md
