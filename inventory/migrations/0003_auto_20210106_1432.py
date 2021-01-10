# Generated by Django 3.1.4 on 2021-01-06 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20210104_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='tags',
            field=models.CharField(blank=True, max_length=700),
        ),
        migrations.AlterField(
            model_name='itemfamily',
            name='tags',
            field=models.CharField(blank=True, max_length=700),
        ),
        migrations.AlterField(
            model_name='itemgroup',
            name='tags',
            field=models.CharField(blank=True, max_length=700),
        ),
        migrations.AlterField(
            model_name='movement',
            name='tags',
            field=models.CharField(blank=True, max_length=700),
        ),
    ]
