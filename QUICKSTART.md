# Nawab UrduVerse - Quick Start Guide

Get started with Nawab UrduVerse in minutes!

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

## Installation (5 Minutes)

### Step 1: Clone the Repository
```bash
git clone https://github.com/nawab/urduverse.git
cd nawab_urduverse
```

### Step 2: Run Setup Script
```bash
python setup.py
```

This will:
- Create a virtual environment
- Install all dependencies
- Create necessary directories
- Run database migrations
- Create a superuser account
- Collect static files
- Start the development server

### Step 3: Access the Application

Open your browser and go to:
- **Website**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Manual Installation

If you prefer manual setup:

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create Environment File
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 7. Run Server
```bash
python manage.py runserver
```

## First Steps

### 1. Access Admin Panel
1. Go to http://127.0.0.1:8000/admin/
2. Login with your superuser credentials
3. Start adding content!

### 2. Add Categories
1. Go to Core > Categories
2. Add categories for Novels, Stories, Poetry, etc.

### 3. Add Authors
1. Go to Core > Authors
2. Add writers and poets

### 4. Add Content
- **Novels**: Novels app > Novels
- **Stories**: Stories app > Stories
- **Poetry**: Poetry app > Poetry
- **Quotes**: Quotes app > Quotes
- **Blog Posts**: Blog app > Blog posts
- **Videos**: Videos app > Videos

## Common Commands

### Development Server
```bash
python manage.py runserver
```

### Create Migrations
```bash
python manage.py makemigrations
```

### Run Migrations
```bash
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Collect Static Files
```bash
python manage.py collectstatic
```

### Shell
```bash
python manage.py shell
```

### Run Tests
```bash
python manage.py test
```

## Project Structure Overview

```
nawab_urduverse/
├── nawab_urduverse/     # Main project settings
├── accounts/            # User authentication
├── core/                # Core functionality
├── novels/              # Novels app
├── stories/             # Stories app
├── poetry/              # Poetry app
├── quotes/              # Quotes app
├── blog/                # Blog app
├── videos/              # Videos app
├── templates/           # HTML templates
├── static/              # CSS, JS, images
└── manage.py            # Django commands
```

## Customization

### Change Site Name
Edit in `nawab_urduverse/settings.py`:
```python
SITE_NAME = 'Your Site Name'
SITE_TAGLINE = 'Your Tagline'
```

### Change Colors
Edit in `static/css/style.css`:
```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
}
```

### Add New Features
1. Create a new app: `python manage.py startapp myapp`
2. Add to `INSTALLED_APPS` in settings
3. Create models, views, and templates
4. Add URL patterns

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8080  # Use different port
```

### Migration Issues
```bash
python manage.py migrate --run-syncdb
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear
```

### Database Issues
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Next Steps

1. **Read the Documentation**
   - [README.md](README.md) - Full documentation
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
   - [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Architecture details

2. **Customize the Theme**
   - Edit `static/css/style.css`
   - Modify templates in `templates/`

3. **Add Content**
   - Use the admin panel to add novels, stories, poetry
   - Upload images and media

4. **Deploy to Production**
   - Follow [DEPLOYMENT.md](DEPLOYMENT.md)
   - Set up PostgreSQL
   - Configure Nginx
   - Enable SSL

## Support

Need help?
- Email: support@nawaburduverse.com
- Website: https://nawaburduverse.com

---

**Happy Coding!** 🚀
