# Generated by Django 3.1.4 on 2021-01-07 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0009_auto_20210106_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=32, null=True, verbose_name='importe'),
        ),
        migrations.AlterField(
            model_name='document',
            name='currency_rate',
            field=models.DecimalField(blank=True, decimal_places=2, default=1, max_digits=10, null=True, verbose_name='tasa de cambio'),
        ),
        migrations.AlterField(
            model_name='document',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=32, null=True, verbose_name='descuento'),
        ),
        migrations.AlterField(
            model_name='document',
            name='tax',
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=32, null=True, verbose_name='impuesto'),
        ),
        migrations.AlterField(
            model_name='document',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=32, null=True, verbose_name='total'),
        ),
    ]
