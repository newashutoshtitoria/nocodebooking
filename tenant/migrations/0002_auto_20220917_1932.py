# Generated by Django 3.2 on 2022-09-17 19:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tenant',
            options={},
        ),
        migrations.RemoveField(
            model_name='tenant',
            name='blog_image',
        ),
        migrations.RemoveField(
            model_name='tenant',
            name='blog_name',
        ),
        migrations.RemoveField(
            model_name='tenant',
            name='description',
        ),
        migrations.RemoveField(
            model_name='tenant',
            name='featured',
        ),
        migrations.RemoveField(
            model_name='tenant',
            name='updated_at',
        ),
    ]
