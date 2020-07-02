# Generated by Django 2.2 on 2020-04-09 20:11

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0039_auto_20200331_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='productbatch',
            name='unit_cost',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=20),
        ),
        migrations.AlterField(
            model_name='productbatch',
            name='batch_ref',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='productbatch',
            name='date_received',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='productbatch',
            name='expiry_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='productbatch',
            name='quantity',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='productbatch',
            name='status',
            field=models.CharField(choices=[('PENDING_ORDER', 'A order which is pending'), ('PENDING_DELIVERY', 'A delivery yet to be made'), ('NOT_ACCEPTED', 'An order which has been cancelled'), ('NOT_RECEIVED', 'An order which is yet to be recieved'), ('NOT_ACCEPTED', 'An order which has yet to be accepted'), ('RETURNED', 'An order which is returned'), ('IN_STOCK', 'Still in stock'), ('OUT_OF_STOCK', 'Out of stock'), ('EXPIRED', 'Expired Products')], default='PENDING_ORDER', max_length=25, null=True),
        ),
    ]
