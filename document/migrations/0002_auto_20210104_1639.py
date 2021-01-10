# Generated by Django 3.1.4 on 2021-01-04 16:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('document', '0001_initial'),
        ('person', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='create_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='document',
            name='doctype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='document.documenttype', verbose_name='tipo'),
        ),
        migrations.AddField(
            model_name='document',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='person.person'),
        ),
        migrations.AddConstraint(
            model_name='documenttype',
            constraint=models.UniqueConstraint(fields=('company', 'code'), name='unique_company_documenttype'),
        ),
        migrations.AddConstraint(
            model_name='document',
            constraint=models.UniqueConstraint(fields=('doctype', 'number'), name='unique_doctype_number'),
        ),
    ]
