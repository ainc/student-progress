# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-09 18:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentgoal',
            options={'ordering': ('-met', '-created_at')},
        ),
        migrations.AddField(
            model_name='studentgoal',
            name='met',
            field=models.BooleanField(default=False),
        ),
    ]
