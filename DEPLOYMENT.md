# Nawab Urdu Academy - Deployment Guide

This guide covers the deployment of Nawab Urdu Academy to a production server.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.9+
- PostgreSQL 12+
- Nginx
- Domain name with SSL certificate

## Server Setup

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages
```bash
sudo apt install -y python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx
sudo apt install -y libpq-dev
sudo apt install -y build-essential
```

### 3. Create Database
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE nawab_urduverse;
CREATE USER nawab_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE nawab_urduverse TO nawab_user;
\q
```

### 4. Create Application User
```bash
sudo useradd -m -s /bin/bash nawab
sudo usermod -aG sudo nawab
```

### 5. Setup Application Directory
```bash
sudo mkdir -p /var/www/nawab_urduverse
sudo chown nawab:nawab /var/www/nawab_urduverse
```

## Application Deployment

### 1. Clone Repository
```bash
cd /var/www/nawab_urduverse
git clone https://github.com/nawab/urduverse.git .
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Environment File
```bash
nano .env
```

Add the following:
```env
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
ALLOWED_HOSTS=nawaburduverse.com,www.nawaburduverse.com

# Database
DB_NAME=nawab_urduverse
DB_USER=nawab_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS S3 (Optional - for media storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 8. Create Media Directory
```bash
mkdir -p media
sudo chown -R nawab:nawab media
```

## Gunicorn Setup

### 1. Create Gunicorn Service
```bash
sudo nano /etc/systemd/system/nawab_urduverse.service
```

Add:
```ini
[Unit]
Description=Nawab Urdu Academy Gunicorn Daemon
After=network.target

[Service]
User=nawab
Group=www-data
WorkingDirectory=/var/www/nawab_urduverse
ExecStart=/var/www/nawab_urduverse/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/var/www/nawab_urduverse/app.sock \
    nawab_urduverse.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 2. Start Gunicorn Service
```bash
sudo systemctl start nawab_urduverse
sudo systemctl enable nawab_urduverse
sudo systemctl status nawab_urduverse
```

## Nginx Configuration

### 1. Create Nginx Config
```bash
sudo nano /etc/nginx/sites-available/nawab_urduverse
```

Add:
```nginx
server {
    listen 80;
    server_name nawaburduverse.com www.nawaburduverse.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/nawab_urduverse;
    }

    location /media/ {
        root /var/www/nawab_urduverse;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/nawab_urduverse/app.sock;
    }
}
```

### 2. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/nawab_urduverse /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Certificate (Let's Encrypt)

### 1. Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obtain Certificate
```bash
sudo certbot --nginx -d nawaburduverse.com -d www.nawaburduverse.com
```

### 3. Auto-renewal
```bash
sudo systemctl status certbot.timer
```

## Performance Optimization

### 1. Database Optimization
```bash
sudo -u postgres psql nawab_urduverse
```

```sql
-- Create indexes for better performance
CREATE INDEX idx_novel_slug ON novels_novel(slug);
CREATE INDEX idx_novel_status ON novels_novel(status);
CREATE INDEX idx_novel_published ON novels_novel(is_published);
CREATE INDEX idx_chapter_novel ON novels_chapter(novel_id);
CREATE INDEX idx_comment_content ON core_comment(content_type, object_id);
```

### 2. Enable Caching
Add to settings.py:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. Install Redis
```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
```

## Monitoring

### 1. Install Logrotate
```bash
sudo nano /etc/logrotate.d/nawab_urduverse
```

Add:
```
/var/www/nawab_urduverse/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 nawab www-data
    sharedscripts
    postrotate
        systemctl reload nawab_urduverse
    endscript
}
```

### 2. Setup Monitoring (Optional)
```bash
# Install monitoring tools
pip install django-prometheus
```

## Backup Strategy

### 1. Database Backup Script
```bash
sudo nano /usr/local/bin/backup_nawab.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/nawab_urduverse"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump nawab_urduverse > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/nawab_urduverse/media

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 2. Make Executable and Schedule
```bash
sudo chmod +x /usr/local/bin/backup_nawab.sh
sudo crontab -e
```

Add:
```
0 2 * * * /usr/local/bin/backup_nawab.sh
```

## Troubleshooting

### Check Logs
```bash
# Gunicorn logs
sudo journalctl -u nawab_urduverse

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Django logs
tail -f /var/www/nawab_urduverse/logs/django.log
```

### Common Issues

1. **Static files not loading**
   - Check `STATIC_ROOT` in settings
   - Run `collectstatic` again
   - Check Nginx configuration

2. **Database connection errors**
   - Verify PostgreSQL is running
   - Check database credentials
   - Ensure user has proper permissions

3. **Permission errors**
   - Check file ownership: `sudo chown -R nawab:nawab /var/www/nawab_urduverse`
   - Check directory permissions

## Updates

### Update Application
```bash
cd /var/www/nawab_urduverse
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart nawab_urduverse
```

## Security Checklist

- [ ] Change default admin URL
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure firewall (ufw)
- [ ] Set up fail2ban
- [ ] Regular security updates
- [ ] Database backups
- [ ] Log monitoring

---

For support, contact: support@nawaburduverse.com
