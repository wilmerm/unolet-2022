# Generated by Django 3.1.4 on 2021-01-24 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0014_auto_20210121_0152'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='entry_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=22, verbose_name='monto introduccido'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=4, editable=False, max_digits=24, verbose_name='monto'),
        ),
    ]
