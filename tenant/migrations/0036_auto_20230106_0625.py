# Generated by Django 3.2 on 2023-01-06 00:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0035_auto_20230106_0616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alltemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 1, 6, 6, 25, 18, 887197), null=True, verbose_name='start date'),
        ),
        migrations.AlterField(
            model_name='otpwallet',
            name='date_transaction',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 6, 6, 25, 18, 889257), verbose_name='transaction date'),
        ),
        migrations.AlterField(
            model_name='subscriptiontransaction',
            name='date_transaction',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 6, 6, 25, 18, 888761), verbose_name='transaction date'),
        ),
        migrations.AlterField(
            model_name='tenantsubscription',
            name='date_billing_start',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 1, 6, 6, 25, 18, 888230), null=True, verbose_name='billing start date'),
        ),
        migrations.AlterField(
            model_name='tenanttemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 1, 6, 6, 25, 18, 887601), null=True, verbose_name='start date'),
        ),
    ]
