# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('tx_lobbying', '0003_auto_20150214_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compensation',
            name='raw',
            field=django.contrib.postgres.fields.hstore.HStoreField(null=True),
        ),
        migrations.AlterField(
            model_name='coversheet',
            name='raw',
            field=django.contrib.postgres.fields.hstore.HStoreField(null=True),
        ),
        migrations.AlterField(
            model_name='expensedetailreport',
            name='raw',
            field=django.contrib.postgres.fields.hstore.HStoreField(null=True),
        ),
        migrations.AlterField(
            model_name='registrationreport',
            name='raw',
            field=django.contrib.postgres.fields.hstore.HStoreField(null=True),
        ),
        migrations.AlterUniqueTogether(
            name='address',
            unique_together=set([('address1', 'city', 'state', 'zipcode')]),
        ),
    ]
