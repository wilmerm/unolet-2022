# Generated by Django 3.1.4 on 2021-01-20 22:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0020_auto_20210120_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='currency_rate',
            field=models.DecimalField(blank=True, decimal_places=4, default=1, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='tasa de cambio'),
        ),
    ]