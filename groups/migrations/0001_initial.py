# Generated by Django 2.1.7 on 2020-10-23 08:51

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
            name='Groups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_created=True)),
                ('group_name', models.TextField()),
                ('entry_code', models.CharField(max_length=8, verbose_name='令牌')),
                ('student_id_list', models.TextField()),
                ('total', models.PositiveIntegerField(default=0, verbose_name='班级人数')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HomeWork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin_time', models.DateTimeField(auto_created=True)),
                ('title', models.TextField()),
                ('end_time', models.DateTimeField(null=True)),
                ('problem_id_list', models.TextField()),
                ('al_achieve', models.PositiveIntegerField(default=0, verbose_name='已经完成作业的人数')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups_by', to='groups.Groups')),
            ],
        ),
        migrations.CreateModel(
            name='HomeWorkRank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('achieve_time', models.DateTimeField(auto_created=True)),
                ('rank_id_list', models.TextField()),
                ('num_limit', models.PositiveIntegerField(default=0)),
                ('homework', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homework_by', to='groups.HomeWork')),
            ],
        ),
    ]