# Generated by Django 2.2 on 2020-03-06 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0031_suppliers_business'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suppliersmeta',
            name='display_name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
