from .settings import DATABASES, BASE_DIR


# Use an isolated SQLite database so makemigrations can run even if the
# checked-in development database has an inconsistent migration history.
DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "migration_autogen.sqlite3",
}
