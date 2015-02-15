# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tx_lobbying', '0002_auto_20150212_0005'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='registrationreport',
            options={'ordering': ('year', 'report_date')},
        ),
        migrations.AddField(
            model_name='interest',
            name='slug',
            field=models.SlugField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lobbyist',
            name='slug',
            field=models.SlugField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
