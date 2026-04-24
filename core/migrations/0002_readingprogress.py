import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_readingprogress_table_if_missing(apps, schema_editor):
    from core.models import ReadingProgress

    existing_tables = set(schema_editor.connection.introspection.table_names())

    if ReadingProgress._meta.db_table not in existing_tables:
        schema_editor.create_model(ReadingProgress)


def drop_readingprogress_table_if_present(apps, schema_editor):
    from core.models import ReadingProgress

    existing_tables = set(schema_editor.connection.introspection.table_names())

    if ReadingProgress._meta.db_table in existing_tables:
        schema_editor.delete_model(ReadingProgress)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        ("novels", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    create_readingprogress_table_if_missing,
                    drop_readingprogress_table_if_present,
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="ReadingProgress",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("progress_percent", models.PositiveIntegerField(default=0, verbose_name="پیش رفت فیصد")),
                        ("last_read_at", models.DateTimeField(auto_now=True, verbose_name="آخری مطالعہ")),
                        ("chapter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="novels.chapter", verbose_name="باب")),
                        ("novel", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="novels.novel", verbose_name="ناول")),
                        ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="صارف")),
                    ],
                    options={
                        "verbose_name": "مطالعہ کی پیش رفت",
                        "verbose_name_plural": "مطالعہ کی پیش رفت",
                        "ordering": ["-last_read_at"],
                    },
                ),
            ],
        ),
    ]
