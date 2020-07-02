# Generated by Django 2.2 on 2020-04-01 19:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0017_salesperformance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesperformance',
            name='receipt',
        ),
        migrations.AddField(
            model_name='salesperformance',
            name='sale',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='sales.Sale'),
        ),
    ]
