# Generated by Django 3.1.4 on 2021-01-06 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_auto_20210106_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='tags',
            field=models.CharField(blank=True, editable=False, max_length=700),
        ),
    ]
