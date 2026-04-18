#!/usr/bin/env bash
set -e

python manage.py migrate --noinput

exec gunicorn nawab_urduverse.wsgi:application
