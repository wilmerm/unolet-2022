# Generated by Django 3.1.4 on 2021-01-20 23:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0010_auto_20210120_2235'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaldocument',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='fecha'),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='expiration_date',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='fecha de vencimiento'),
        ),
    ]
