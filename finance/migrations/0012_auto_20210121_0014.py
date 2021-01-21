# Generated by Django 3.1.4 on 2021-01-21 00:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0008_auto_20210111_1225'),
        ('finance', '0011_auto_20210120_2235'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='person',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='person.person', verbose_name='Persona'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='person_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='nombre de la persona'),
        ),
    ]
