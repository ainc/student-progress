# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-15 20:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0007_studentguardian_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship',
            name='student_approved',
            field=models.BooleanField(default=False),
        ),
    ]
