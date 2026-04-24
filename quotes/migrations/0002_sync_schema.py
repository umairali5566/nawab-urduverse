from django.db import migrations


def sync_quotes_schema(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())
    Quote = apps.get_model("quotes", "Quote")
    QuoteCollection = apps.get_model("quotes", "QuoteCollection")

    if Quote._meta.db_table not in existing_tables:
        schema_editor.create_model(Quote)
        existing_tables = set(connection.introspection.table_names())

    quote_categories_through = Quote._meta.get_field("categories").remote_field.through
    if quote_categories_through._meta.db_table not in existing_tables:
        schema_editor.create_model(quote_categories_through)
        existing_tables = set(connection.introspection.table_names())

    if QuoteCollection._meta.db_table not in existing_tables:
        schema_editor.create_model(QuoteCollection)
        existing_tables = set(connection.introspection.table_names())

    quote_collection_through = QuoteCollection._meta.get_field("quotes").remote_field.through
    if quote_collection_through._meta.db_table not in existing_tables:
        schema_editor.create_model(quote_collection_through)


class Migration(migrations.Migration):

    dependencies = [
        ("quotes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(sync_quotes_schema, migrations.RunPython.noop),
    ]
