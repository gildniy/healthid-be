# Generated by Django 2.2 on 2020-04-19 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0013_auto_20200419_1613'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transferbatch',
            old_name='batch',
            new_name='product_batch',
        ),
    ]
