# Generated by Django 2.2 on 2020-02-18 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0005_auto_20191202_0954'),
        ('orders', '0030_auto_20200212_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='suppliers',
            name='business',
            field=models.ManyToManyField(to='business.Business'),
        ),
    ]