#!/usr/bin/env python
"""
Nawab UrduVerse - Setup Script
Automated setup for development environment
"""

import os
import sys
import subprocess
import argparse
from importlib.util import find_spec


def run_command(command, description=""):
    """Run a shell command"""
    if description:
        print(f"\n{'='*60}")
        print(f"{description}")
        print(f"{'='*60}")
    
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    
    if result.returncode != 0:
        print(f"Error: Command failed with return code {result.returncode}")
        return False
    return True


def create_virtual_environment():
    """Create virtual environment"""
    if os.path.exists("venv"):
        print("Virtual environment already exists.")
        return True
    
    return run_command("python3 -m venv venv", "Creating Virtual Environment")


def install_dependencies():
    """Install Python dependencies"""
    pip_cmd = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing Dependencies")


def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists(".env"):
        print(".env file already exists.")
        return True
    
    env_content = """# Nawab UrduVerse - Environment Configuration
DEBUG=True
SECRET_KEY=change-this-in-production-to-a-secure-random-string
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Email (Console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("Created .env file. Please update it with your settings.")
    return True


def run_migrations():
    """Run Django migrations"""
    python_cmd = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python"
    return run_command(f"{python_cmd} manage.py migrate", "Running Migrations")


def create_superuser():
    """Create Django superuser"""
    python_cmd = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python"
    
    print("\n" + "="*60)
    print("Creating Superuser")
    print("="*60)
    
    return run_command(f"{python_cmd} manage.py createsuperuser")


def collect_static():
    """Collect static files"""
    python_cmd = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python"
    return run_command(f"{python_cmd} manage.py collectstatic --noinput", "Collecting Static Files")


def create_directories():
    """Create necessary directories"""
    directories = [
        "media",
        "media/novels/covers",
        "media/stories",
        "media/poetry/backgrounds",
        "media/quotes/backgrounds",
        "media/videos/thumbnails",
        "media/authors",
        "media/avatars",
        "media/blog",
        "static/images",
        "logs",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("Created necessary directories.")
    return True


def run_server():
    """Run Django development server"""
    python_cmd = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python"
    sslserver_available = find_spec("sslserver") is not None
    cert_exists = os.path.exists("cert.pem")
    key_exists = os.path.exists("key.pem")
    use_https = sslserver_available and cert_exists and key_exists
    protocol = "https" if use_https else "http"
    server_command = f"{python_cmd} manage.py runserver --https" if use_https else f"{python_cmd} manage.py runserver"
    
    print("\n" + "="*60)
    print("Starting Development Server")
    print("="*60)
    print(f"Access the application at: {protocol}://127.0.0.1:8000/")
    print(f"Admin panel at: {protocol}://127.0.0.1:8000/admin/")
    if not use_https:
        if not sslserver_available:
            print("Tip: install django-sslserver to enable HTTPS development mode.")
        elif not cert_exists or not key_exists:
            print("Tip: add cert.pem and key.pem in the project root to enable HTTPS development mode.")
    print("="*60 + "\n")
    
    return run_command(server_command)


def main():
    parser = argparse.ArgumentParser(description="Nawab UrduVerse Setup")
    parser.add_argument("--skip-superuser", action="store_true", help="Skip creating superuser")
    parser.add_argument("--skip-server", action="store_true", help="Skip running server")
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              Nawab UrduVerse - Setup Script                  ║
    ║                                                              ║
    ║         A Complete Urdu Literature Platform                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required.")
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Creating Virtual Environment", create_virtual_environment),
        ("Installing Dependencies", install_dependencies),
        ("Creating Environment File", create_env_file),
        ("Creating Directories", create_directories),
        ("Running Migrations", run_migrations),
    ]
    
    if not args.skip_superuser:
        steps.append(("Creating Superuser", create_superuser))
    
    steps.append(("Collecting Static Files", collect_static))
    
    # Run setup steps
    for name, func in steps:
        if not func():
            print(f"\nSetup failed at step: {name}")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("Setup completed successfully!")
    print("="*60)
    
    if not args.skip_server:
        run_server()
    else:
        print("\nTo start the server, run:")
        print("  python manage.py runserver")


if __name__ == "__main__":
    main()
