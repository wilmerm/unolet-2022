# Generated by Django 3.1.4 on 2021-01-15 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0014_auto_20210114_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='pay_taxes',
            field=models.BooleanField(default=True, help_text='Determina si este documento paga impuestos.', verbose_name='Paga impuestos'),
        ),
    ]