# Generated by Django 3.2 on 2023-02-05 08:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_useraddress_address_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='packagecheckout',
            name='checkout',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='package_checkouts', to='main.checkout'),
        ),
    ]
