# Generated by Django 3.1.4 on 2021-01-25 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0012_auto_20210124_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalitem',
            name='is_service',
            field=models.BooleanField(default=False, verbose_name='es un artículo de servicio'),
        ),
    ]