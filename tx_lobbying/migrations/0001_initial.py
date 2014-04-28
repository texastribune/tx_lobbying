# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lobbyist',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('filer_id', models.IntegerField(unique=True)),
                ('updated_at', models.DateField()),
                ('name', models.CharField(max_length=100)),
                ('sort_name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=45)),
                ('last_name', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=15)),
                ('suffix', models.CharField(max_length=5)),
                ('nick_name', models.CharField(max_length=25)),
            ],
            options={
                u'ordering': ('sort_name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Interest',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('state', models.CharField(max_length=2)),
            ],
            options={
                u'ordering': ('name',),
                u'unique_together': set([('name', 'state')]),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExpenseCoversheet',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('lobbyist', models.ForeignKey(to='tx_lobbying.Lobbyist', to_field=u'id')),
                ('raw', models.TextField()),
                ('report_date', models.DateField()),
                ('report_id', models.IntegerField(unique=True)),
                ('year', models.IntegerField()),
                ('transportation', models.DecimalField(default='0.00', verbose_name='Transportation & Lodging', max_digits=12, decimal_places=2)),
                ('food', models.DecimalField(default='0.00', verbose_name='Food & Beverages', max_digits=12, decimal_places=2)),
                ('entertainment', models.DecimalField(default='0.00', verbose_name='Entertainment', max_digits=12, decimal_places=2)),
                ('gifts', models.DecimalField(default='0.00', verbose_name='Gifts', max_digits=12, decimal_places=2)),
                ('awards', models.DecimalField(default='0.00', verbose_name='Awards & Memementos', max_digits=12, decimal_places=2)),
                ('events', models.DecimalField(default='0.00', verbose_name='Political Fundraiers / Charity Events', max_digits=12, decimal_places=2)),
                ('media', models.DecimalField(default='0.00', verbose_name='Mass Media Communications', max_digits=12, decimal_places=2)),
                ('ben_senators', models.DecimalField(default='0.00', verbose_name='State Senators', max_digits=12, decimal_places=2)),
                ('ben_representatives', models.DecimalField(default='0.00', verbose_name='State Representatives', max_digits=12, decimal_places=2)),
                ('ben_other', models.DecimalField(default='0.00', verbose_name='Other Elected/Appointed Officials', max_digits=12, decimal_places=2)),
                ('ben_legislative', models.DecimalField(default='0.00', verbose_name='Legislative Branch Employees', max_digits=12, decimal_places=2)),
                ('ben_executive', models.DecimalField(default='0.00', verbose_name='Executive Agency Employees', max_digits=12, decimal_places=2)),
                ('ben_family', models.DecimalField(default='0.00', verbose_name='Family of Legis/Exec Branch', max_digits=12, decimal_places=2)),
                ('ben_events', models.DecimalField(default='0.00', verbose_name='Events - All Legis Invited', max_digits=12, decimal_places=2)),
                ('ben_guests', models.DecimalField(default='0.00', verbose_name='Guests', max_digits=12, decimal_places=2)),
                ('total_spent', models.DecimalField(default='0.00', max_digits=13, decimal_places=2)),
                ('total_benefited', models.DecimalField(default='0.00', max_digits=13, decimal_places=2)),
                ('spent_guess', models.DecimalField(default='0.00', max_digits=13, decimal_places=2)),
            ],
            options={
                u'ordering': ('report_date',),
            },
            bases=(models.Model,),
        ),
    ]
