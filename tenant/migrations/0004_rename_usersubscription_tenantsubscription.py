# Generated by Django 3.2 on 2022-10-24 15:29

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscriptionplansg', '0001_initial'),
        ('tenant', '0003_usersubscription_teant_attched'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserSubscription',
            new_name='TenantSubscription',
        ),
    ]