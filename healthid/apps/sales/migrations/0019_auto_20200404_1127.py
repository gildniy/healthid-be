# Generated by Django 2.2 on 2020-04-04 10:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0018_auto_20200401_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesperformance',
            name='cashier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_cashier', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='salesperformance',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_customer', to='profiles.Profile'),
        ),
        migrations.AlterField(
            model_name='salesperformance',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_product', to='products.Product'),
        ),
        migrations.AlterField(
            model_name='salesperformance',
            name='sale',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='sales.Sale'),
        ),
    ]
