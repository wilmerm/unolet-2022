# Generated by Django 3.1.4 on 2021-01-15 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='note',
            field=models.CharField(blank=True, max_length=500, verbose_name='nota'),
        ),
    ]
