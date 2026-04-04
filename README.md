# Nawab UrduVerse

**A Complete Urdu Literature Platform by Nawab**

Nawab UrduVerse is a modern, scalable, and feature-rich web application for Urdu literature enthusiasts. It provides a comprehensive platform for reading Urdu novels, stories, poetry, quotes, blogs, and watching related videos.

## Features

### Content Sections
- **Novels**: Chapter-based reading system with categories (Romantic, Islamic, Horror, Social, Historical)
- **Stories**: Short Urdu stories with category filtering
- **Poetry**: Ghazal, Nazm, Shayari with mood-based filtering (Love, Sad, etc.)
- **Quotes**: Urdu quotes with images, Islamic and motivational quotes
- **Blog**: SEO-optimized articles with tags and categories
- **Videos**: Poetry videos, story narration with YouTube embedding
- **Authors**: Writer and poet profiles with complete bibliography

### User Features
- User registration and authentication
- User profiles with bookmarks
- Comment system
- Reading progress tracking
- Dark mode support
- Mobile responsive design
- RTL (Right-to-Left) Urdu text layout

### Admin Features
- Complete admin panel for content management
- Novel and chapter management
- Story, poetry, and quote publishing
- Author management
- Category management
- Comment moderation
- SEO tools

### SEO Features
- SEO-friendly URLs
- Meta titles and descriptions
- XML sitemap
- Structured data
- Fast page loading
- Social media sharing

## Technology Stack

- **Backend**: Python Django 4.2+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5 (RTL)
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Rich Text**: CKEditor
- **Fonts**: Noto Nastaliq Urdu, Noto Naskh Arabic

## Project Structure

```
nawab_urduverse/
├── nawab_urduverse/          # Main project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                  # User authentication
├── core/                      # Core functionality
├── novels/                    # Novels app
├── stories/                   # Stories app
├── poetry/                    # Poetry app
├── quotes/                    # Quotes app
├── blog/                      # Blog app
├── videos/                    # Videos app
├── templates/                 # HTML templates
├── static/                    # CSS, JS, images
├── media/                     # User uploaded files
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites
- Python 3.9+
- pip
- virtualenv (recommended)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/nawab/urduverse.git
cd nawab_urduverse
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Database setup**
```bash
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Collect static files**
```bash
python manage.py collectstatic
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Website: http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL for production)
DB_NAME=nawab_urduverse
DB_USER=nawab_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

### Production Deployment

1. Set `DEBUG=False` in settings
2. Configure PostgreSQL database
3. Set up static files with whitenoise or CDN
4. Configure email backend
5. Set up SSL certificate
6. Use gunicorn or uWSGI as WSGI server

## Database Models

### Core Models
- **Category**: Content categories
- **Tag**: Content tags
- **Author**: Writers and poets
- **Comment**: User comments
- **Bookmark**: User bookmarks
- **ReadingProgress**: Track reading progress

### Content Models
- **Novel**: Novels with chapters
- **Chapter**: Novel chapters
- **Story**: Short stories
- **Poetry**: Poems and ghazals
- **Quote**: Urdu quotes
- **BlogPost**: Blog articles
- **Video**: Embedded videos

## API Endpoints

### Authentication
- `/accounts/register/` - User registration
- `/accounts/login/` - User login
- `/accounts/logout/` - User logout
- `/accounts/profile/` - User profile

### Content
- `/novels/` - Novel list
- `/stories/` - Story list
- `/poetry/` - Poetry list
- `/quotes/` - Quote list
- `/blog/` - Blog list
- `/videos/` - Video list

### Search
- `/search/?q=query` - Global search

### API
- `/bookmark/<type>/<id>/` - Add/remove bookmark
- `/comment/<type>/<id>/` - Add comment

## Customization

### Themes
- Edit `static/css/style.css` for custom styling
- Edit `static/css/dark-mode.css` for dark theme

### Templates
- All templates are in `templates/` directory
- Base template: `templates/base.html`
- App-specific templates in respective folders

### Static Files
- CSS: `static/css/`
- JavaScript: `static/js/`
- Images: `static/images/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is proprietary and developed for **Nawab**.
All rights reserved.

## Support

For support and inquiries, contact:
- Email: support@nawaburduverse.com
- Website: https://nawaburduverse.com

## Credits

- **Developer**: Nawab Team
- **Design**: Nawab Creative Studio
- **Fonts**: Google Fonts (Noto Nastaliq Urdu)
- **Icons**: Bootstrap Icons

---

**Powered by Django | Made with ❤️ by Nawab**
