# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0007_auto_20160305_1934'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='responses',
            name='trainee',
        ),
    ]
