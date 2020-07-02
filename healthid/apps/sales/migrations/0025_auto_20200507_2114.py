# Generated by Django 2.2 on 2020-05-07 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0024_auto_20200507_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='payment_method',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Credit', 'Credit'), ('Card', 'Card'), ('Bank Transfer', 'Bank_Transfer')], max_length=18),
        ),
    ]
