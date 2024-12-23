# Generated by Django 2.2 on 2020-05-05 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0045_order_outlet'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplierorder',
            name='additional_notes',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='supplierorder',
            name='delivery_promptness',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='supplierorder',
            name='service_quality',
            field=models.PositiveIntegerField(default=3),
        ),
    ]
