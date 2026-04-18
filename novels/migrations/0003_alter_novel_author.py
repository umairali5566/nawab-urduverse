from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('novels', '0002_novel_core_relationships'),
    ]

    operations = [
        migrations.AlterField(
            model_name='novel',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='novels',
                to='core.author',
                verbose_name='Ù…ØµÙ†Ù',
            ),
        ),
    ]
