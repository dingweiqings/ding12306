# Generated by Django 3.0.5 on 2020-05-24 12:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_admin', '0011_auto_20200524_2019'),
    ]

    operations = [
        migrations.AddField(
            model_name='waituser',
            name='order',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='queryjob',
            name='state',
            field=models.IntegerField(choices=[(0, 'NEW'), (1, 'START'), (2, 'RUNNING'), (3, 'BLOCK'), (4, 'END')], default=0),
        ),
        migrations.AlterField(
            model_name='waituser',
            name='job_key',
            field=models.CharField(max_length=36),
        ),
        migrations.AlterField(
            model_name='waituser',
            name='left_date',
            field=models.DateField(default=datetime.datetime(2020, 5, 24, 20, 57, 26, 940538)),
        ),
        migrations.AlterField(
            model_name='waituser',
            name='state',
            field=models.IntegerField(choices=[(0, 'NEW'), (1, 'START'), (2, 'RUNNING'), (3, 'BLOCK'), (4, 'END')], default=0),
        ),
    ]
