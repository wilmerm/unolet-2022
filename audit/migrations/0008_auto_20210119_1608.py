# Generated by Django 3.1.4 on 2021-01-19 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0007_historicaldocument_historicaldocumenttype_historicalidentificationtype_historicalitem_historicalitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaldocument',
            name='sequence',
            field=models.IntegerField(default=1, editable=False, verbose_name='secuencia'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='historicaldocument',
            name='number',
            field=models.CharField(blank=True, max_length=30, verbose_name='número'),
        ),
    ]
