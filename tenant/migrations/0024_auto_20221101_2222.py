# Generated by Django 3.2 on 2022-11-01 16:52

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenant', '0023_auto_20221101_2221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alltemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 11, 1, 22, 22, 46, 77663), null=True, verbose_name='start date'),
        ),
        migrations.AlterField(
            model_name='otpwallet',
            name='date_transaction',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 1, 22, 22, 46, 79510), verbose_name='transaction date'),
        ),
        migrations.AlterField(
            model_name='otpwallet',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='otp_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='subscriptiontransaction',
            name='date_transaction',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 1, 22, 22, 46, 79006), verbose_name='transaction date'),
        ),
        migrations.AlterField(
            model_name='tenantsubscription',
            name='date_billing_start',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 11, 1, 22, 22, 46, 78475), null=True, verbose_name='billing start date'),
        ),
        migrations.AlterField(
            model_name='tenanttemplate',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 11, 1, 22, 22, 46, 78033), null=True, verbose_name='start date'),
        ),
    ]
