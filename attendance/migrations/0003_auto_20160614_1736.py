# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-14 17:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_auto_20160609_1836'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('skill_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Subskill',
            fields=[
                ('sub_id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=1000)),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Skill')),
            ],
        ),
        migrations.AlterModelOptions(
            name='studentgoal',
            options={'ordering': ('met', 'created_at')},
        ),
    ]