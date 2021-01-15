# Generated by Django 3.1.4 on 2021-01-14 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0013_auto_20210111_1320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documenttype',
            name='inventory',
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='generic_type',
            field=models.CharField(choices=[('invoice', 'Factura'), ('invoice_return', 'Devolución en factura'), ('purchase', 'Compra'), ('purchase_order', 'Orden de compra'), ('quotation', 'Cotización'), ('inventory_input', 'Entrada de inventario'), ('inventory_output', 'Salida de inventario'), ('transfer', 'Transferencia de inventario'), ('accounting_income', 'Ingreso contable'), ('accounting_expense', 'Gasto contable')], help_text='tipo genérico al que pertenece.', max_length=20, verbose_name='tipo genérico'),
        ),
        migrations.DeleteModel(
            name='TransferDocument',
        ),
    ]
