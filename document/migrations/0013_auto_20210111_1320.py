# Generated by Django 3.1.4 on 2021-01-11 13:20

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import document.models
import unoletutils.libs.text


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0008_auto_20210111_1225'),
        ('finance', '0005_auto_20210106_1432'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('warehouse', '0003_auto_20210106_1432'),
        ('document', '0012_auto_20210110_1957'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tags', models.CharField(blank=True, editable=False, max_length=700)),
                ('number', models.IntegerField(editable=False, verbose_name='número')),
                ('person_name', models.CharField(blank=True, max_length=100, verbose_name='nombre de la persona')),
                ('note', models.CharField(blank=True, max_length=500, verbose_name='nota')),
                ('currency_rate', models.DecimalField(blank=True, decimal_places=2, default=1, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='tasa de cambio')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=32, null=True, verbose_name='importe')),
                ('discount', models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=32, null=True, verbose_name='descuento')),
                ('tax', models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=32, null=True, verbose_name='impuesto')),
                ('total', models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=32, null=True, verbose_name='total')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('create_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('currency', models.ForeignKey(default=document.models.get_default_currency, null=True, on_delete=django.db.models.deletion.PROTECT, to='finance.currency', verbose_name='moneda')),
                ('doctype', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='document.documenttype', verbose_name='tipo')),
                ('person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='person.person')),
                ('tax_receipt_number', models.OneToOneField(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='finance.taxreceiptnumber', verbose_name='Número de comprobante fiscal')),
                ('transfer_warehouse', models.ForeignKey(blank=True, default=None, help_text='almacén a transferir.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transferdocument2_set', to='warehouse.warehouse')),
                ('warehouse', models.ForeignKey(help_text='almacén del documento.', on_delete=django.db.models.deletion.CASCADE, to='warehouse.warehouse')),
            ],
            bases=(models.Model, unoletutils.libs.text.Text),
        ),
        migrations.AddConstraint(
            model_name='transferdocument',
            constraint=models.UniqueConstraint(fields=('doctype', 'number'), name='unique_transferdocument'),
        ),
    ]
