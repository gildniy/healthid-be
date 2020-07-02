# Generated by Django 2.1.7 on 2019-05-07 11:57

from django.db import migrations, models
import django.db.models.deletion
import healthid.utils.app_utils.id_generator


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20190502_1257'),
        ('outlets', '0004_outlet_preference'),
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.CharField(default=healthid.utils.app_utils.id_generator.id_gen, editable=False, max_length=9, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=140, unique=True)),
                ('description', models.TextField()),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('outlet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='outlets.Outlet')),
                ('products', models.ManyToManyField(blank=True, to='products.Product')),
            ],
        ),
        migrations.CreateModel(
            name='PromotionType',
            fields=[
                ('id', models.CharField(default=healthid.utils.app_utils.id_generator.id_gen, editable=False, max_length=9, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=140, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='promotion',
            name='promotion_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.PromotionType'),
        ),
    ]
