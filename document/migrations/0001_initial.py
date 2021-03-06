# Generated by Django 3.1.4 on 2021-01-04 16:39

from django.db import migrations, models
import django.db.models.deletion
import unoletutils.libs.text


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tags', models.CharField(max_length=700)),
                ('number', models.IntegerField(editable=False, verbose_name='número')),
                ('person_name', models.CharField(blank=True, max_length=100, verbose_name='nombre de la persona')),
                ('note', models.CharField(blank=True, max_length=500, verbose_name='nota')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=32, null=True, verbose_name='importe')),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=32, null=True, verbose_name='descuento')),
                ('tax', models.DecimalField(blank=True, decimal_places=2, max_digits=32, null=True, verbose_name='impuesto')),
                ('total', models.DecimalField(blank=True, decimal_places=2, max_digits=32, null=True, verbose_name='total')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
            ],
            options={
                'verbose_name': 'documento',
                'verbose_name_plural': 'documentos',
            },
            bases=(models.Model, unoletutils.libs.text.Text),
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tags', models.CharField(max_length=700)),
                ('code', models.CharField(max_length=6, verbose_name='código')),
                ('name', models.CharField(max_length=70, verbose_name='nombre')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company', verbose_name='Empresa')),
            ],
            options={
                'verbose_name': 'tipo de documento',
                'verbose_name_plural': 'tipos de documentos',
            },
            bases=(models.Model, unoletutils.libs.text.Text),
        ),
    ]
