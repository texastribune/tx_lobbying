# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tx_lobbying', '0004_interest_zipcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='interest',
            name='address2',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='interest',
            name='address1',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='interest',
            name='city',
            field=models.CharField(max_length=75, null=True, blank=True),
            preserve_default=True,
        ),
    ]
