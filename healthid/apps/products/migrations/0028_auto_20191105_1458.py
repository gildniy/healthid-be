# Generated by Django 2.2 on 2019-11-05 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('outlets', '0009_auto_20190710_0911'),
        ('products', '0027_batchinfo_is_returnable'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='measurement_unit',
            new_name='dispensing_size',
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('product_name', 'manufacturer', 'outlet', 'description', 'dispensing_size')},
        ),
    ]
