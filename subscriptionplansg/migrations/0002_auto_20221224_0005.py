# Generated by Django 3.2 on 2022-12-23 18:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptionplansg', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='planlistdetail',
            name='plan',
        ),
        migrations.RemoveField(
            model_name='planlistdetail',
            name='plan_list',
        ),
        migrations.DeleteModel(
            name='PlanList',
        ),
        migrations.DeleteModel(
            name='PlanListDetail',
        ),
    ]
