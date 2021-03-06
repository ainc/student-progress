# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-15 19:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0005_skill_font_awesome_icon'),
    ]

    operations = [
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('relation_id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='studentguardian',
            name='student',
        ),
        migrations.AddField(
            model_name='relationship',
            name='guardian',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.StudentGuardian'),
        ),
        migrations.AddField(
            model_name='relationship',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Student'),
        ),
    ]
