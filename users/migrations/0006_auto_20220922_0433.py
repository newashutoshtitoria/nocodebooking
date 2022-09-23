# Generated by Django 3.2 on 2022-09-21 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_rename_sent_on_requestednewphonenumber_created_on'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='phone_validated',
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['phone_number'], name='users_user_phone_n_7fe504_idx'),
        ),
    ]