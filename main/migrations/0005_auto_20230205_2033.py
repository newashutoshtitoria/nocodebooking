# Generated by Django 3.2 on 2023-02-05 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20230205_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkout',
            name='package_stages',
            field=models.CharField(blank=True, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='address_type',
            field=models.CharField(blank=True, choices=[('Others', 'Others'), ('Home', 'Home')], max_length=20, null=True),
        ),
    ]
