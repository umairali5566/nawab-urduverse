from django.db import migrations


def sync_blog_schema(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())
    BlogCategory = apps.get_model("blog", "BlogCategory")
    BlogPost = apps.get_model("blog", "BlogPost")

    if BlogCategory._meta.db_table not in existing_tables:
        schema_editor.create_model(BlogCategory)
        existing_tables.add(BlogCategory._meta.db_table)

    if BlogPost._meta.db_table not in existing_tables:
        schema_editor.create_model(BlogPost)


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(sync_blog_schema, migrations.RunPython.noop),
    ]
