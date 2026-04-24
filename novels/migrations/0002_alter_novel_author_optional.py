import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("novels", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="novel",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="novels",
                to="core.author",
                verbose_name="مصنف",
            ),
        ),
    ]
