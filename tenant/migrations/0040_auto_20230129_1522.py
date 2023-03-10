# Generated by Django 3.2 on 2023-01-29 09:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0039_auto_20230129_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alltemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 1, 29, 15, 22, 30, 852998), null=True, verbose_name='start date'),
        ),
        migrations.AlterField(
            model_name='otpwallet',
            name='date_transaction',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 29, 15, 22, 30, 854725), verbose_name='transaction date'),
        ),
        migrations.AlterField(
            model_name='subscriptiontransaction',
            name='date_transaction',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 29, 15, 22, 30, 854312), verbose_name='transaction date'),
        ),
        migrations.AlterField(
            model_name='tenantsubscription',
            name='date_billing_start',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 1, 29, 15, 22, 30, 853867), null=True, verbose_name='billing start date'),
        ),
        migrations.AlterField(
            model_name='tenanttemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 1, 29, 15, 22, 30, 853348), null=True, verbose_name='start date'),
        ),
    ]
