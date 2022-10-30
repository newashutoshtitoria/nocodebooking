# Generated by Django 3.2 on 2022-10-30 10:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0016_auto_20221030_1559'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tenanttemplate',
            name='paid_template',
        ),
        migrations.AlterField(
            model_name='alltemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 10, 30, 16, 13, 58, 459020), null=True, verbose_name='start date'),
        ),
        migrations.AlterField(
            model_name='subscriptiontransaction',
            name='date_transaction',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 30, 16, 13, 58, 460142), verbose_name='transaction date'),
        ),
        migrations.AlterField(
            model_name='tenantsubscription',
            name='date_billing_start',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 10, 30, 16, 13, 58, 459708), null=True, verbose_name='billing start date'),
        ),
        migrations.AlterField(
            model_name='tenanttemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 10, 30, 16, 13, 58, 459340), null=True, verbose_name='start date'),
        ),
    ]
