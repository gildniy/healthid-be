# Generated by Django 2.2 on 2019-11-21 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_orderdetails_supplier_order_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetails',
            name='cost_per_item',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='supplier_order_name',
            field=models.CharField(editable=False, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='price',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
