# Generated by Django 2.2 on 2020-04-08 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0021_auto_20200407_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesperformance',
            name='transaction_date',
            field=models.DateTimeField(),
        ),
    ]
