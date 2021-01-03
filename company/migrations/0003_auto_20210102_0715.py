# Generated by Django 3.1.4 on 2021-01-02 07:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0002_auto_20210102_0328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='admin_users',
            field=models.ManyToManyField(blank=True, related_name='admin_users_company_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='company',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]