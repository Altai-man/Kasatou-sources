# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Layers', '0003_remove_user_thread_per_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
    ]
