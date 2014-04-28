# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tx_lobbying', '0002_compensation_expensedetailreport_intereststats_lobbyiststat_lobbyistyear_registrationreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='compensation',
            name='year',
            field=models.ForeignKey(to='tx_lobbying.LobbyistYear', to_field=u'id'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='compensation',
            unique_together=set([('year', 'interest')]),
        ),
    ]
