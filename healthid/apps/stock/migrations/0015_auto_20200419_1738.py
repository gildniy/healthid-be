# Generated by Django 2.2 on 2020-04-19 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0014_auto_20200419_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocktransfer',
            name='status',
            field=models.CharField(choices=[('STARTED', 'Incomplete transfer'), ('IN_TRANSIT', 'Awaiting confirmation'), ('RECEIVED', 'Transferred stock')], default='STARTED', max_length=50),
        ),
    ]
