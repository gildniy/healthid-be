# Generated by Django 2.2 on 2020-03-08 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0033_auto_20200305_1703'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='suppliers',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='supplierscontacts',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='suppliersmeta',
            name='parent',
        ),
    ]
