# Generated by Django 3.1.4 on 2021-01-21 01:50

from django.db import migrations, models
import django.db.models.deletion
import unoletutils.libs.text


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0003_company_logo'),
        ('finance', '0012_auto_20210121_0014'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['-create_date'], 'verbose_name': 'transacción', 'verbose_name_plural': 'transacciones'},
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='nombre')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company', verbose_name='Empresa')),
            ],
            options={
                'verbose_name': 'forma de pago',
                'verbose_name_plural': 'formas de pagos',
            },
            bases=(models.Model, unoletutils.libs.text.Text),
        ),
        migrations.AddField(
            model_name='transaction',
            name='payment_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='finance.paymentmethod', verbose_name='forma de pago'),
        ),
        migrations.AddConstraint(
            model_name='paymentmethod',
            constraint=models.UniqueConstraint(fields=('company', 'name'), name='unique_paymentmethod_name'),
        ),
    ]
