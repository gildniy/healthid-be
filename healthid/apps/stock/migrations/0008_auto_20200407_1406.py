# Generated by Django 2.2 on 2020-04-07 13:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import healthid.utils.app_utils.id_generator


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0006_userbusiness'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0038_auto_20200324_1425'),
        ('stock', '0007_auto_20190916_1214'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stocktransfer',
            old_name='destination_outlet',
            new_name='destination',
        ),
        migrations.RenameField(
            model_name='stocktransfer',
            old_name='sending_outlet',
            new_name='source',
        ),
        migrations.RemoveField(
            model_name='stocktransfer',
            name='complete_status',
        ),
        migrations.RemoveField(
            model_name='stocktransfer',
            name='product',
        ),
        migrations.RemoveField(
            model_name='stocktransfer',
            name='stock_transfer_record',
        ),
        migrations.AddField(
            model_name='stocktransfer',
            name='business',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='stock_transfer', to='business.Business'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stocktransfer',
            name='date_dispatched',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='stocktransfer',
            name='date_received',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='stocktransfer',
            name='initiated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='initiated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stocktransfer',
            name='received_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='received_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stocktransfer',
            name='status',
            field=models.CharField(default='Incomplete transfer', max_length=50),
        ),
        migrations.AlterField(
            model_name='stocktransfer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.CreateModel(
            name='TransferBatch',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('id', models.CharField(default=healthid.utils.app_utils.id_generator.id_gen, editable=False, max_length=9, primary_key=True, serialize=False)),
                ('unit_cost', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('quantity_sent', models.PositiveIntegerField(default=0)),
                ('quantity_received', models.PositiveIntegerField(default=0)),
                ('expiry_date', models.DateField(null=True)),
                ('comments', models.CharField(max_length=200)),
                ('batch_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.BatchInfo')),
                ('deleted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product')),
                ('stock_transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_batch', to='stock.StockTransfer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]