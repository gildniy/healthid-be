# Generated by Django 2.2 on 2020-03-24 13:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0037_batchinfo_outlet_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='batchinfo',
            old_name='outlet_id',
            new_name='outlet',
        ),
    ]
