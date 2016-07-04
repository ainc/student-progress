# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-15 01:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_auto_20160614_1736'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentProgress',
            fields=[
                ('progress_id', models.AutoField(primary_key=True, serialize=False)),
                ('achieved', models.BooleanField(default=False)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Student')),
                ('subskill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Subskill')),
            ],
        ),
    ]