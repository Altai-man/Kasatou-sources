# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import Layers.models
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasePost',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, max_length=5000)),
                ('date', models.DateTimeField(verbose_name='%Y-%m-%d %H:%M:%S', auto_now_add=True)),
                ('archive', models.FileField(blank=True, upload_to='documents')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('board_name', models.CharField(max_length=3)),
                ('thread_max_post', models.IntegerField(default=500)),
                ('is_moderated', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('code', models.CharField(max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('basepost_ptr', models.OneToOneField(to='Layers.BasePost', parent_link=True, primary_key=True, auto_created=True, serialize=False)),
                ('topic', models.CharField(blank=True, max_length=40)),
                ('image1', models.ImageField(blank=True, upload_to=Layers.models.content_file_name)),
                ('image2', models.ImageField(blank=True, upload_to=Layers.models.content_file_name)),
                ('image3', models.ImageField(blank=True, upload_to=Layers.models.content_file_name)),
            ],
            options={
            },
            bases=('Layers.basepost',),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('basepost_ptr', models.OneToOneField(to='Layers.BasePost', parent_link=True, primary_key=True, auto_created=True, serialize=False)),
                ('post_count', models.IntegerField(default=0)),
                ('update_time', models.DateTimeField(verbose_name='%Y-%m-%d %H:%M:%S', auto_now_add=True)),
                ('topic', models.CharField(max_length=40)),
                ('image1', models.ImageField(upload_to=Layers.models.content_file_name)),
                ('image2', models.ImageField(blank=True, upload_to=Layers.models.content_file_name)),
            ],
            options={
            },
            bases=('Layers.basepost',),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('email', models.EmailField(verbose_name='Email', unique=True, max_length=255)),
                ('theme', models.CharField(default='Light', max_length=10)),
                ('name', models.CharField(default='Anonymous', max_length=14)),
                ('thread_per_page', models.IntegerField(default=8)),
                ('liked_threads', models.CharField(default='', max_length=50)),
                ('date_joined', models.DateTimeField(verbose_name='Date joined', default=django.utils.timezone.now)),
                ('invites_count', models.IntegerField(default=3)),
                ('is_admin', models.BooleanField(verbose_name='Admin status', default=False)),
                ('is_active', models.BooleanField(verbose_name='Active', default=True)),
                ('groups', models.ManyToManyField(related_name='user_set', to='auth.Group', verbose_name='groups', related_query_name='user', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.')),
                ('user_permissions', models.ManyToManyField(related_name='user_set', to='auth.Permission', verbose_name='user permissions', related_query_name='user', blank=True, help_text='Specific permissions for this user.')),
            ],
            options={
                'verbose_name': 'Anonymous',
                'verbose_name_plural': 'Anonymouses',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='post',
            name='thread_id',
            field=models.ForeignKey(to='Layers.Thread'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invite',
            name='sender',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basepost',
            name='board_id',
            field=models.ForeignKey(to='Layers.Board'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basepost',
            name='user_id',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
