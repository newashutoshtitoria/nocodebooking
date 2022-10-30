# Generated by Django 3.2 on 2022-10-28 18:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0014_auto_20221029_0009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alltemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 10, 29, 0, 9, 43, 78643), null=True, verbose_name='start date'),
        ),
        migrations.AlterField(
            model_name='subscriptiontransaction',
            name='date_transaction',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 29, 0, 9, 43, 79734), verbose_name='transaction date'),
        ),
        migrations.AlterField(
            model_name='tenantsubscription',
            name='date_billing_start',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 10, 29, 0, 9, 43, 79298), null=True, verbose_name='billing start date'),
        ),
        migrations.AlterField(
            model_name='tenanttemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 10, 29, 0, 9, 43, 78945), null=True, verbose_name='start date'),
        ),
    ]
