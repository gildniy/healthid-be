# Generated by Django 2.1.7 on 2019-07-15 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0005_auto_20190712_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockcounttemplate',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='stockcounttemplate',
            name='status',
            field=models.CharField(default='Scheduled in advance', max_length=50),
        ),
    ]
