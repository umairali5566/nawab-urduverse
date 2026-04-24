from django.db import migrations


def sync_videos_schema(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())
    Video = apps.get_model("videos", "Video")
    VideoPlaylist = apps.get_model("videos", "VideoPlaylist")

    if Video._meta.db_table not in existing_tables:
        schema_editor.create_model(Video)
        existing_tables = set(connection.introspection.table_names())

    if VideoPlaylist._meta.db_table not in existing_tables:
        schema_editor.create_model(VideoPlaylist)
        existing_tables = set(connection.introspection.table_names())

    playlist_through = VideoPlaylist._meta.get_field("videos").remote_field.through
    if playlist_through._meta.db_table not in existing_tables:
        schema_editor.create_model(playlist_through)


class Migration(migrations.Migration):

    dependencies = [
        ("videos", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(sync_videos_schema, migrations.RunPython.noop),
    ]
