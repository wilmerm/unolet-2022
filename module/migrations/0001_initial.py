# Generated by Django 3.1.4 on 2020-12-28 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70, verbose_name='nombre')),
                ('description', models.CharField(blank=True, max_length=200, verbose_name='descripción')),
            ],
            options={
                'verbose_name': 'módulo',
                'verbose_name_plural': 'módulos',
            },
        ),
    ]