# Generated by Django 2.2 on 2020-03-20 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0035_auto_20200206_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='global_upc',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
