# Generated by Django 3.2 on 2022-10-27 15:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0004_rename_usersubscription_tenantsubscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenantsubscription',
            name='date_billing_start',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 10, 27, 20, 54, 34, 82191), null=True, verbose_name='billing start date'),
        ),
    ]