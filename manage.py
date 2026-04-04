#!/usr/bin/env python
"""
Nawab Urdu Academy - Django Management Script
A complete Urdu literature platform by Nawab
"""

import os
import sys
from importlib.util import find_spec
from pathlib import Path


def _parse_env_bool(name, default=False):
    """Read a boolean environment variable."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _rewrite_dev_server_args(argv):
    """
    Route `runserver` to HTTPS automatically when local certs are present.
    Flags:
    - --https: force HTTPS
    - --http: force plain HTTP
    Env:
    - DEVSERVER_USE_HTTPS=true/false
    - DEVSERVER_CERT / DEVSERVER_KEY
    """
    if len(argv) < 2 or argv[1] != "runserver":
        return argv

    force_https = "--https" in argv
    force_http = "--http" in argv
    cleaned_argv = [arg for arg in argv if arg not in {"--https", "--http"}]

    cert_path = Path(os.environ.get("DEVSERVER_CERT", "cert.pem"))
    key_path = Path(os.environ.get("DEVSERVER_KEY", "key.pem"))
    auto_https_default = cert_path.exists() and key_path.exists()
    env_prefers_https = _parse_env_bool("DEVSERVER_USE_HTTPS", default=auto_https_default)
    wants_https = not force_http and (force_https or env_prefers_https)

    if not wants_https:
        return cleaned_argv

    if find_spec("sslserver") is None:
        print(
            "Warning: HTTPS dev server requested, but 'django-sslserver' is not installed. "
            "Starting HTTP runserver instead."
        )
        return cleaned_argv

    rewritten = [cleaned_argv[0], "runsslserver", *cleaned_argv[2:]]
    has_certificate = any(arg in {"--certificate", "--cert"} for arg in rewritten)
    has_key = "--key" in rewritten

    if cert_path.exists() and not has_certificate:
        rewritten.extend(["--certificate", str(cert_path)])
    if key_path.exists() and not has_key:
        rewritten.extend(["--key", str(key_path)])

    print("Starting HTTPS development server. Use '--http' to force plain HTTP.")
    return rewritten


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nawab_urduverse.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(_rewrite_dev_server_args(sys.argv))


if __name__ == '__main__':
    main()
