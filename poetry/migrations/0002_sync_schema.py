from django.db import migrations


def sync_poetry_schema(apps, schema_editor):
    connection = schema_editor.connection
    introspection = connection.introspection
    existing_tables = set(introspection.table_names())

    Poetry = apps.get_model("poetry", "Poetry")
    PoetryCollection = apps.get_model("poetry", "PoetryCollection")

    def get_columns(table_name):
        with connection.cursor() as cursor:
            description = introspection.get_table_description(cursor, table_name)
        return {column.name for column in description}

    poetry_table = Poetry._meta.db_table
    if poetry_table not in existing_tables:
        schema_editor.create_model(Poetry)
        existing_tables.add(poetry_table)
    else:
        poetry_columns = get_columns(poetry_table)
        for field_name in ("views_count", "likes_count"):
            field = Poetry._meta.get_field(field_name)
            if field.column not in poetry_columns:
                schema_editor.add_field(Poetry, field)
                poetry_columns.add(field.column)

    collection_table = PoetryCollection._meta.db_table
    if collection_table not in existing_tables:
        schema_editor.create_model(PoetryCollection)
        existing_tables = set(introspection.table_names())

    through_model = PoetryCollection._meta.get_field("poems").remote_field.through
    through_table = through_model._meta.db_table
    if through_table not in existing_tables:
        schema_editor.create_model(through_model)


class Migration(migrations.Migration):

    dependencies = [
        ("poetry", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(sync_poetry_schema, migrations.RunPython.noop),
    ]
