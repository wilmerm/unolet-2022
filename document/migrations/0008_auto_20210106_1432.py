# Generated by Django 3.1.4 on 2021-01-06 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0007_document_warehouse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='tags',
            field=models.CharField(blank=True, max_length=700),
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='tags',
            field=models.CharField(blank=True, max_length=700),
        ),
    ]