# Generated by Django 3.1.4 on 2021-01-17 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_item_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='available',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, editable=False, max_digits=22, verbose_name='disponible'),
        ),
        migrations.AddField(
            model_name='item',
            name='max_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=22, verbose_name='precio máximo'),
        ),
        migrations.AddField(
            model_name='item',
            name='min_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=22, verbose_name='precio mínimo'),
        ),
    ]
