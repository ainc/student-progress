# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-25 20:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='class',
            options={'verbose_name_plural': 'Class'},
        ),
    ]
