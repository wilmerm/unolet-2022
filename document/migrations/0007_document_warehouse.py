# Generated by Django 3.1.4 on 2021-01-06 02:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0001_initial'),
        ('document', '0006_document_tax_receipt_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='warehouse',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='warehouse.warehouse'),
            preserve_default=False,
        ),
    ]
