# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address1', models.CharField(max_length=200, null=True, blank=True)),
                ('address2', models.CharField(max_length=200, null=True, blank=True)),
                ('city', models.CharField(max_length=75, null=True, blank=True)),
                ('state', models.CharField(max_length=2)),
                ('zipcode', models.CharField(max_length=11, null=True, blank=True)),
                ('coordinate', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('coordinate_quality', models.CharField(max_length=2, null=True, blank=True)),
                ('canonical', models.ForeignKey(related_name='aliases', blank=True, to='tx_lobbying.Address', null=True)),
            ],
            options={
                'ordering': ('address1',),
                'verbose_name_plural': 'addresses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Compensation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw', models.TextField()),
                ('amount_high', models.IntegerField()),
                ('amount_low', models.IntegerField()),
                ('compensation_type', models.CharField(max_length=20, null=True, blank=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('updated_at', models.DateField()),
                ('amount_guess', models.IntegerField()),
                ('address', models.ForeignKey(blank=True, to='tx_lobbying.Address', help_text=b'The address the lobbyist listed for the `Interest`', null=True)),
            ],
            options={
                'ordering': ('interest__name', 'annum__year', 'annum__lobbyist'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Coversheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw', models.TextField()),
                ('report_date', models.DateField()),
                ('report_id', models.PositiveIntegerField(unique=True)),
                ('correction', models.PositiveSmallIntegerField(default=0, help_text=b'Correction Number (0=Original)')),
                ('year', models.PositiveSmallIntegerField()),
                ('transportation', models.DecimalField(default=0, verbose_name=b'Transportation & Lodging', max_digits=12, decimal_places=2)),
                ('food', models.DecimalField(default=0, verbose_name=b'Food & Beverages', max_digits=12, decimal_places=2)),
                ('entertainment', models.DecimalField(default=0, verbose_name=b'Entertainment', max_digits=12, decimal_places=2)),
                ('gifts', models.DecimalField(default=0, verbose_name=b'Gifts', max_digits=12, decimal_places=2)),
                ('awards', models.DecimalField(default=0, verbose_name=b'Awards & Memementos', max_digits=12, decimal_places=2)),
                ('events', models.DecimalField(default=0, verbose_name=b'Political Fundraiers / Charity Events', max_digits=12, decimal_places=2)),
                ('media', models.DecimalField(default=0, verbose_name=b'Mass Media Communications', max_digits=12, decimal_places=2)),
                ('ben_senators', models.DecimalField(default=0, verbose_name=b'State Senators', max_digits=12, decimal_places=2)),
                ('ben_representatives', models.DecimalField(default=0, verbose_name=b'State Representatives', max_digits=12, decimal_places=2)),
                ('ben_other', models.DecimalField(default=0, verbose_name=b'Other Elected/Appointed Officials', max_digits=12, decimal_places=2)),
                ('ben_legislative', models.DecimalField(default=0, verbose_name=b'Legislative Branch Employees', max_digits=12, decimal_places=2)),
                ('ben_executive', models.DecimalField(default=0, verbose_name=b'Executive Agency Employees', max_digits=12, decimal_places=2)),
                ('ben_family', models.DecimalField(default=0, verbose_name=b'Family of Legis/Exec Branch', max_digits=12, decimal_places=2)),
                ('ben_events', models.DecimalField(default=0, verbose_name=b'Events - All Legis Invited', max_digits=12, decimal_places=2)),
                ('ben_guests', models.DecimalField(default=0, verbose_name=b'Guests', max_digits=12, decimal_places=2)),
                ('total_spent', models.DecimalField(default=0, max_digits=13, decimal_places=2)),
                ('total_benefited', models.DecimalField(default=0, max_digits=13, decimal_places=2)),
                ('spent_guess', models.DecimalField(default=b'0.00', help_text=b'max(total_spent, total_benefited)', max_digits=13, decimal_places=2)),
            ],
            options={
                'ordering': ('report_date',),
                'get_latest_by': 'year',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExpenseDetailReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw', models.TextField()),
                ('idno', models.PositiveIntegerField()),
                ('year', models.IntegerField()),
                ('amount', models.DecimalField(default=0, null=True, max_digits=12, decimal_places=2)),
                ('type', models.CharField(max_length=20)),
                ('amount_guess', models.DecimalField(default=0, max_digits=12, decimal_places=2)),
                ('cover', models.ForeignKey(related_name='details', to='tx_lobbying.Coversheet')),
            ],
            options={
                'ordering': ('cover__report_date',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Interest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('nomenklatura_id', models.PositiveIntegerField(null=True, blank=True)),
                ('address', models.ForeignKey(to='tx_lobbying.Address')),
                ('canonical', models.ForeignKey(related_name='aliases', blank=True, to='tx_lobbying.Interest', null=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InterestStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(null=True, blank=True)),
                ('guess', models.IntegerField(null=True, blank=True)),
                ('high', models.IntegerField(null=True, blank=True)),
                ('low', models.IntegerField(null=True, blank=True)),
                ('lobbyist_count', models.IntegerField(null=True, blank=True)),
                ('interest', models.ForeignKey(related_name='stats', to='tx_lobbying.Interest')),
            ],
            options={
                'ordering': ('year',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Lobbyist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filer_id', models.IntegerField(unique=True)),
                ('updated_at', models.DateField()),
                ('name', models.CharField(max_length=100)),
                ('sort_name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=45)),
                ('last_name', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=15)),
                ('suffix', models.CharField(max_length=5)),
                ('nick_name', models.CharField(max_length=25)),
                ('address', models.ForeignKey(blank=True, to='tx_lobbying.Address', null=True)),
            ],
            options={
                'ordering': ('sort_name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LobbyistAnnum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField()),
                ('clients', models.ManyToManyField(related_name='years_available', through='tx_lobbying.Compensation', to='tx_lobbying.Interest')),
                ('lobbyist', models.ForeignKey(related_name='years', to='tx_lobbying.Lobbyist')),
            ],
            options={
                'ordering': ('-year',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LobbyistStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField()),
                ('transportation', models.DecimalField(default=b'0.00', verbose_name=b'Transportation & Lodging', max_digits=12, decimal_places=2)),
                ('food', models.DecimalField(default=b'0.00', verbose_name=b'Food & Beverages', max_digits=12, decimal_places=2)),
                ('entertainment', models.DecimalField(default=b'0.00', verbose_name=b'Entertainment', max_digits=12, decimal_places=2)),
                ('gifts', models.DecimalField(default=b'0.00', verbose_name=b'Gifts', max_digits=12, decimal_places=2)),
                ('awards', models.DecimalField(default=b'0.00', verbose_name=b'Awards & Memementos', max_digits=12, decimal_places=2)),
                ('events', models.DecimalField(default=b'0.00', verbose_name=b'Political Fundraiers / Charity Events', max_digits=12, decimal_places=2)),
                ('media', models.DecimalField(default=b'0.00', verbose_name=b'Mass Media Communications', max_digits=12, decimal_places=2)),
                ('ben_senators', models.DecimalField(default=b'0.00', verbose_name=b'State Senators', max_digits=12, decimal_places=2)),
                ('ben_representatives', models.DecimalField(default=b'0.00', verbose_name=b'State Representatives', max_digits=12, decimal_places=2)),
                ('ben_other', models.DecimalField(default=b'0.00', verbose_name=b'Other Elected/Appointed Officials', max_digits=12, decimal_places=2)),
                ('ben_legislative', models.DecimalField(default=b'0.00', verbose_name=b'Legislative Branch Employees', max_digits=12, decimal_places=2)),
                ('ben_executive', models.DecimalField(default=b'0.00', verbose_name=b'Executive Agency Employees', max_digits=12, decimal_places=2)),
                ('ben_family', models.DecimalField(default=b'0.00', verbose_name=b'Family of Legis/Exec Branch', max_digits=12, decimal_places=2)),
                ('ben_events', models.DecimalField(default=b'0.00', verbose_name=b'Events - All Legis Invited', max_digits=12, decimal_places=2)),
                ('ben_guests', models.DecimalField(default=b'0.00', verbose_name=b'Guests', max_digits=12, decimal_places=2)),
                ('total_spent', models.DecimalField(default=b'0.00', max_digits=13, decimal_places=2)),
                ('total_benefited', models.DecimalField(default=b'0.00', max_digits=13, decimal_places=2)),
                ('spent_guess', models.DecimalField(default=b'0.00', max_digits=13, decimal_places=2)),
                ('lobbyist', models.ForeignKey(related_name='stats', to='tx_lobbying.Lobbyist')),
            ],
            options={
                'ordering': ('year',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegistrationReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw', models.TextField()),
                ('report_id', models.IntegerField(unique=True)),
                ('report_date', models.DateField()),
                ('year', models.IntegerField()),
                ('address', models.ForeignKey(to='tx_lobbying.Address')),
                ('lobbyist', models.ForeignKey(related_name='registrations', to='tx_lobbying.Lobbyist')),
            ],
            options={
                'ordering': ('year',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category_id', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=50)),
                ('other_description', models.CharField(max_length=50, blank=True)),
                ('name', models.CharField(help_text='Human curated name', max_length=50, null=True, blank=True)),
                ('slug', models.SlugField(unique=True, null=True, blank=True)),
            ],
            options={
                'ordering': ('category_id', 'slug'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='lobbyiststats',
            unique_together=set([('lobbyist', 'year')]),
        ),
        migrations.AlterUniqueTogether(
            name='lobbyistannum',
            unique_together=set([('lobbyist', 'year')]),
        ),
        migrations.AlterUniqueTogether(
            name='intereststats',
            unique_together=set([('interest', 'year')]),
        ),
        migrations.AddField(
            model_name='expensedetailreport',
            name='lobbyist',
            field=models.ForeignKey(related_name='expensedetails', to='tx_lobbying.Lobbyist'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='expensedetailreport',
            unique_together=set([('idno', 'type')]),
        ),
        migrations.AddField(
            model_name='coversheet',
            name='lobbyist',
            field=models.ForeignKey(related_name='coversheets', to='tx_lobbying.Lobbyist'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coversheet',
            name='subjects',
            field=models.ManyToManyField(related_name='reports', to='tx_lobbying.Subject'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='compensation',
            name='annum',
            field=models.ForeignKey(to='tx_lobbying.LobbyistAnnum'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='compensation',
            name='interest',
            field=models.ForeignKey(to='tx_lobbying.Interest'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='compensation',
            unique_together=set([('annum', 'interest')]),
        ),
    ]
