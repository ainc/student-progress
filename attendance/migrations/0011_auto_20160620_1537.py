# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-20 15:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0010_coach_profile_img_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coach',
            name='profile_img_url',
            field=models.CharField(default='https://avatars3.githubusercontent.com/u/3189845?v=3&s=460', max_length=150),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='profile_img_url',
            field=models.CharField(default='https://avatars3.githubusercontent.com/u/3189845?v=3&s=460', max_length=150),
        ),
    ]