# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tx_lobbying', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='compensation',
            name='report',
            field=models.ForeignKey(blank=True, to='tx_lobbying.RegistrationReport', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registrationreport',
            name='address',
            field=models.ForeignKey(help_text=b'The address the lobbyist listed for themself.', to='tx_lobbying.Address'),
            preserve_default=True,
        ),
    ]
