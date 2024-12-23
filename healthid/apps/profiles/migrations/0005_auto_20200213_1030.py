# Generated by Django 2.2 on 2020-02-13 09:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0005_auto_20191202_0954'),
        ('profiles', '0004_auto_20200115_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='business',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='business.Business'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='email',
            field=models.EmailField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='primary_mobile_number',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
