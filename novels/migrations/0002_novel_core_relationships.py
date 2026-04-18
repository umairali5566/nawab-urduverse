from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('novels', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='author',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='novels',
                to='core.author',
                verbose_name='Ù…ØµÙ†Ù',
            ),
        ),
        migrations.AddField(
            model_name='novel',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='core.category',
                verbose_name='Ø²Ù…Ø±Û',
            ),
        ),
    ]
