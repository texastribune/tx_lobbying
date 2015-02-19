# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tx_lobbying', '0003_auto_20150214_2135'),
    ]

    operations = [
        migrations.AddField(
            model_name='lobbyist',
            name='score',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
