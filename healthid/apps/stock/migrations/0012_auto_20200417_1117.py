# Generated by Django 2.2 on 2020-04-17 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0011_auto_20200415_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transferbatch',
            name='stock_transfer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock.StockTransfer'),
        ),
    ]