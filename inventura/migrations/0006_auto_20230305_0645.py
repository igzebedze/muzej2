# Generated by Django 3.2.15 on 2023-03-05 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventura', '0005_auto_20230302_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalstran',
            name='stevilo_besed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='stran',
            name='stevilo_besed',
            field=models.IntegerField(default=0),
        ),
    ]