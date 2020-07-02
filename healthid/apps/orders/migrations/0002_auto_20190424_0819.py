# Generated by Django 2.1.7 on 2019-04-24 07:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import healthid.utils.app_utils.id_generator


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='suppliers',
            name='admin_comment',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='suppliers',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='suppliers',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='proposedEdit', to='orders.Suppliers'),
        ),
        migrations.AddField(
            model_name='suppliers',
            name='user',
            field=models.ForeignKey(
                default='aul5xrp73', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='suppliers',
            name='email',
            field=models.EmailField(max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='suppliers',
            name='id',
            field=models.CharField(default=healthid.utils.app_utils.id_generator.id_gen,
                                   editable=False, max_length=9, primary_key=True, serialize=False),
        ),
    ]