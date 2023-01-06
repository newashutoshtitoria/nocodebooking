# Generated by Django 3.2 on 2023-01-06 00:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0033_auto_20230101_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alltemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 1, 6, 5, 39, 26, 571638), null=True, verbose_name='start date'),
        ),
        migrations.AlterField(
            model_name='otpwallet',
            name='date_transaction',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 6, 5, 39, 26, 573341), verbose_name='transaction date'),
        ),
        migrations.AlterField(
            model_name='subscriptiontransaction',
            name='date_transaction',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 6, 5, 39, 26, 572930), verbose_name='transaction date'),
        ),
        migrations.AlterField(
            model_name='tenantsubscription',
            name='date_billing_start',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 1, 6, 5, 39, 26, 572483), null=True, verbose_name='billing start date'),
        ),
        migrations.AlterField(
            model_name='tenanttemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 1, 6, 5, 39, 26, 571962), null=True, verbose_name='start date'),
        ),
    ]
