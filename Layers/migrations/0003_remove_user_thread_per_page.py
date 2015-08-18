# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Layers', '0002_remove_user_liked_threads'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='thread_per_page',
        ),
    ]
