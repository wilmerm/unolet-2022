# Generated by Django 3.1.4 on 2021-01-20 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0019_documentnote_create_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documentnote',
            options={'ordering': ['-create_date'], 'verbose_name': 'nota', 'verbose_name_plural': 'notas'},
        ),
    ]
