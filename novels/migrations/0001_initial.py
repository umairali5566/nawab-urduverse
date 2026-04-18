import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Novel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300, verbose_name='Ø¹Ù†ÙˆØ§Ù†')),
                ('slug', models.SlugField(unique=True, verbose_name='Ø³Ù„Ú¯')),
                ('content', models.TextField(verbose_name='Ù…ÙˆØ§Ø¯')),
                ('is_published', models.BooleanField(default=True, verbose_name='Ø´Ø§Ø¦Ø¹ Ø´Ø¯Û')),
                ('published_at', models.DateTimeField(blank=True, null=True, verbose_name='Ø´Ø§Ø¦Ø¹ ÛÙˆÙ†Û’ Ú©ÛŒ ØªØ§Ø±ÛŒØ®')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Ù†Ø§ÙˆÙ„',
                'verbose_name_plural': 'Ù†Ø§ÙˆÙ„Ø²',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NovelReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='Ø±ÛŒÙ¹Ù†Ú¯')),
                ('review_text', models.TextField(verbose_name='Ø¬Ø§Ø¦Ø²Û')),
                ('is_approved', models.BooleanField(default=True, verbose_name='Ù…Ù†Ø¸ÙˆØ± Ø´Ø¯Û')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('novel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='novels.novel', verbose_name='Ù†Ø§ÙˆÙ„')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ØµØ§Ø±Ù')),
            ],
            options={
                'verbose_name': 'Ø¬Ø§Ø¦Ø²Û',
                'verbose_name_plural': 'Ø¬Ø§Ø¦Ø²Û’',
                'ordering': ['-created_at'],
                'unique_together': {('novel', 'user')},
            },
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chapter_number', models.PositiveIntegerField(verbose_name='Ø¨Ø§Ø¨ Ù†Ù…Ø¨Ø±')),
                ('title', models.CharField(max_length=300, verbose_name='Ø¹Ù†ÙˆØ§Ù†')),
                ('slug', models.SlugField(verbose_name='Ø³Ù„Ú¯')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Ù…ÙˆØ§Ø¯')),
                ('is_published', models.BooleanField(default=True, verbose_name='Ø´Ø§Ø¦Ø¹ Ø´Ø¯Û')),
                ('is_premium', models.BooleanField(default=False, verbose_name='Ù¾Ø±ÛŒÙ…ÛŒÙ…')),
                ('views_count', models.PositiveIntegerField(default=0, verbose_name='Ù…Ø´Ø§ÛØ¯Ø§Øª')),
                ('word_count', models.PositiveIntegerField(default=0, verbose_name='Ø§Ù„ÙØ§Ø¸ Ú©ÛŒ ØªØ¹Ø¯Ø§Ø¯')),
                ('reading_time', models.PositiveIntegerField(default=0, verbose_name='Ù¾Ú‘Ú¾Ù†Û’ Ú©Ø§ ÙˆÙ‚Øª (Ù…Ù†Ù¹)')),
                ('published_at', models.DateTimeField(blank=True, null=True, verbose_name='Ø´Ø§Ø¦Ø¹ ÛÙˆÙ†Û’ Ú©ÛŒ ØªØ§Ø±ÛŒØ®')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('meta_title', models.CharField(blank=True, max_length=200, verbose_name='Ù…ÛŒÙ¹Ø§ Ø¹Ù†ÙˆØ§Ù†')),
                ('meta_description', models.TextField(blank=True, verbose_name='Ù…ÛŒÙ¹Ø§ ØªÙØµÛŒÙ„')),
                ('novel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chapters', to='novels.novel', verbose_name='Ù†Ø§ÙˆÙ„')),
            ],
            options={
                'verbose_name': 'Ø¨Ø§Ø¨',
                'verbose_name_plural': 'Ø§Ø¨ÙˆØ§Ø¨',
                'ordering': ['chapter_number'],
                'unique_together': {('novel', 'chapter_number')},
            },
        ),
    ]
