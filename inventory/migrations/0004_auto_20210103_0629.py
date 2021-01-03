# Generated by Django 3.1.4 on 2021-01-03 06:29

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import inventory.models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
        ('inventory', '0003_movement_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='movement',
            name='currency',
            field=models.ForeignKey(default=inventory.models.get_default_currency, null=True, on_delete=django.db.models.deletion.PROTECT, to='finance.currency', verbose_name='moneda'),
        ),
        migrations.AddField(
            model_name='movement',
            name='currency_rate',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='tasa de cambio'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='discount',
            field=models.DecimalField(decimal_places=2, max_digits=22, validators=[django.core.validators.MinValueValidator(0)], verbose_name='descuento'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=22, validators=[django.core.validators.MinValueValidator(0)], verbose_name='precio'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name='cantidad'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='tax',
            field=models.DecimalField(decimal_places=2, max_digits=22, validators=[django.core.validators.MinValueValidator(0)], verbose_name='impuesto'),
        ),
    ]