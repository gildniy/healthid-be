# Generated by Django 2.2 on 2020-06-22 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0034_sale_return_sale_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payments',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True),
        ),
    ]
