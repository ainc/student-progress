# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-08 19:22
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('record_id', models.AutoField(primary_key=True, serialize=False)),
                ('attended', models.BooleanField()),
                ('note', models.CharField(default='', max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('class_id', models.AutoField(primary_key=True, serialize=False)),
                ('class_name', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name_plural': 'Class',
            },
        ),
        migrations.CreateModel(
            name='ClassSession',
            fields=[
                ('session_id', models.AutoField(primary_key=True, serialize=False)),
                ('class_date', models.DateTimeField(verbose_name='Class date')),
                ('_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Class')),
            ],
        ),
        migrations.CreateModel(
            name='Coach',
            fields=[
                ('coach_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Coaches',
            },
        ),
        migrations.CreateModel(
            name='CoachNote',
            fields=[
                ('note_id', models.AutoField(primary_key=True, serialize=False)),
                ('note', models.CharField(max_length=1000)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Coach')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('enroll_id', models.AutoField(primary_key=True, serialize=False)),
                ('_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Class')),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Coach')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('student_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='StudentGoal',
            fields=[
                ('goal_id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=1000)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Student')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='StudentGuardian',
            fields=[
                ('guardian_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Student')),
            ],
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('profile_id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=60)),
                ('phone', models.CharField(max_length=11)),
                ('github_user_name', models.CharField(max_length=30)),
                ('bio', models.CharField(max_length=140)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Student profiles',
            },
        ),
        migrations.AddField(
            model_name='student',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='attendance.StudentProfile'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Student'),
        ),
        migrations.AddField(
            model_name='coachnote',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Student'),
        ),
        migrations.AddField(
            model_name='classsession',
            name='coach',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Coach'),
        ),
        migrations.AddField(
            model_name='attendancerecord',
            name='_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Class'),
        ),
        migrations.AddField(
            model_name='attendancerecord',
            name='coach',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Coach'),
        ),
        migrations.AddField(
            model_name='attendancerecord',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.ClassSession'),
        ),
        migrations.AddField(
            model_name='attendancerecord',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Student'),
        ),
    ]
