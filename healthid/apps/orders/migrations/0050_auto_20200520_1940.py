# Generated by Django 2.2 on 2020-05-20 18:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('outlets', '0013_merge_20200421_1903'),
        ('orders', '0049_auto_20200520_1936'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='supplieroutletcontacts',
            unique_together={('supplier', 'outlet', 'dataKey')},
        ),
    ]
