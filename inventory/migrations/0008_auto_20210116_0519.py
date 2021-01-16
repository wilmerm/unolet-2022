# Generated by Django 3.1.4 on 2021-01-16 05:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_auto_20210115_1308'),
    ]

    operations = [
        migrations.AddField(
            model_name='movement',
            name='name',
            field=models.CharField(blank=True, max_length=70, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='number',
            field=models.IntegerField(default=1, editable=False, verbose_name='número'),
        ),
        migrations.AlterField(
            model_name='movement',
            name='tax',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, editable=False, max_digits=22, validators=[django.core.validators.MinValueValidator(0)], verbose_name='impuesto'),
        ),
    ]
