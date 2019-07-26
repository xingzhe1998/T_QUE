# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-10 02:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0005_userlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlog',
            name='update_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='回答时间'),
            preserve_default=False,
        ),
    ]
