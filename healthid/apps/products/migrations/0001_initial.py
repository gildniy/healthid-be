# Generated by Django 2.1.7 on 2019-04-16 12:04

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0001_initial'),
        ('taggit', '0003_taggeditem_add_unique_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeasurementUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=244, unique=True)),
                ('pack_size', models.CharField(max_length=50)),
                ('sku_number', models.CharField(max_length=100)),
                ('is_approved', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=150)),
                ('brand', models.CharField(max_length=50)),
                ('manufacturer', models.CharField(max_length=50)),
                ('vat_status', models.CharField(max_length=50)),
                ('quality', models.CharField(max_length=50)),
                ('sales_price', models.IntegerField()),
                ('created_date', models.DateField(auto_now=True)),
                ('nearest_expiry_date', models.DateField(null=True)),
                ('backup_supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='backup', to='orders.Suppliers')),
                ('measurement_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.MeasurementUnit')),
                ('prefered_supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prefered', to='orders.Suppliers')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='product_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.ProductCategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
