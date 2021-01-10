# Generated by Django 3.1.4 on 2021-01-04 19:00

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import document.models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
        ('document', '0002_auto_20210104_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='currency',
            field=models.ForeignKey(default=document.models.get_default_currency, null=True, on_delete=django.db.models.deletion.PROTECT, to='finance.currency', verbose_name='moneda'),
        ),
        migrations.AddField(
            model_name='document',
            name='currency_rate',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='tasa de cambio'),
        ),
    ]
