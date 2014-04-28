# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tx_lobbying', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseDetailReport',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('idno', models.IntegerField()),
                ('cover', models.ForeignKey(to='tx_lobbying.ExpenseCoversheet', to_field=u'id')),
                ('lobbyist', models.ForeignKey(to='tx_lobbying.Lobbyist', to_field=u'id')),
                ('year', models.IntegerField()),
                ('amount', models.DecimalField(default='0.00', null=True, max_digits=12, decimal_places=2)),
                ('type', models.CharField(max_length=20)),
                ('amount_guess', models.DecimalField(default='0.00', max_digits=12, decimal_places=2)),
                ('raw', models.TextField()),
            ],
            options={
                u'ordering': ('cover__report_date',),
                u'unique_together': set([('idno', 'type')]),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InterestStats',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('interest', models.ForeignKey(to='tx_lobbying.Interest', to_field=u'id')),
                ('year', models.IntegerField(null=True, blank=True)),
                ('guess', models.IntegerField(null=True, blank=True)),
                ('high', models.IntegerField(null=True, blank=True)),
                ('low', models.IntegerField(null=True, blank=True)),
                ('lobbyist_count', models.IntegerField(null=True, blank=True)),
            ],
            options={
                u'unique_together': set([('interest', 'year')]),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LobbyistStat',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('lobbyist', models.ForeignKey(to='tx_lobbying.Lobbyist', to_field=u'id')),
                ('year', models.IntegerField()),
                ('spent', models.DecimalField(default='0.00', max_digits=13, decimal_places=2)),
            ],
            options={
                u'ordering': ('year',),
                u'unique_together': set([('lobbyist', 'year')]),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegistrationReport',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('lobbyist', models.ForeignKey(to='tx_lobbying.Lobbyist', to_field=u'id')),
                ('report_id', models.IntegerField(unique=True)),
                ('report_date', models.DateField()),
                ('year', models.IntegerField()),
                ('raw', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Compensation',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount_high', models.IntegerField()),
                ('amount_low', models.IntegerField()),
                ('interest', models.ForeignKey(to='tx_lobbying.Interest', to_field=u'id')),
                ('raw', models.TextField()),
                ('updated_at', models.DateField()),
                ('amount_guess', models.IntegerField()),
            ],
            options={
                u'ordering': ('interest__name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LobbyistYear',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('lobbyist', models.ForeignKey(to='tx_lobbying.Lobbyist', to_field=u'id')),
                ('year', models.IntegerField()),
                ('clients', models.ManyToManyField(to='tx_lobbying.Interest', through='tx_lobbying.Compensation')),
            ],
            options={
                u'ordering': ('-year',),
                u'unique_together': set([('lobbyist', 'year')]),
            },
            bases=(models.Model,),
        ),
    ]
