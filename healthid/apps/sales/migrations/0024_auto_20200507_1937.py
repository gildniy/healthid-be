# Generated by Django 2.2 on 2020-05-07 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0023_auto_20200507_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='payment_method',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Credit', 'Credit'), ('Card', 'Card'), ('Bank Transfer', 'Bank Transfer')], max_length=18),
        ),
    ]
