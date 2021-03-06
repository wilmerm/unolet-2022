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
            name='Warehouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tags', models.CharField(max_length=700)),
                ('name', models.CharField(help_text='nombre para el público.', max_length=100, verbose_name='nombre')),
                ('address', models.CharField(blank=True, max_length=500, verbose_name='dirección')),
                ('phones', models.CharField(blank=True, max_length=100, verbose_name='teléfonos')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='correo electrónico')),
                ('is_active', models.BooleanField(default=True, verbose_name='activo')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company', verbose_name='Empresa')),
            ],
            options={
                'verbose_name': 'almacén',
                'verbose_name_plural': 'almacenes',
                'ordering': ['company', 'is_active', 'name'],
            },
            bases=(models.Model, unoletutils.libs.text.Text),
        ),
    ]
