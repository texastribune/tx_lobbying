# -*- coding: utf-8 -*-
from collections import defaultdict, namedtuple

from django.contrib.gis.db import models as geo_models
from django.contrib.postgres.fields import HStoreField
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count, Sum, Q
from django.template import Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from djchoices import DjangoChoices, ChoiceItem


##########
# MIXINS #
##########

class RawDataMixin(models.Model):
    """For models that store raw data."""
    raw = HStoreField(null=True)

    class Meta:
        abstract = True


##########
# MODELS #
##########
class Address(geo_models.Model):
    """
    A US address.

    You'll see some places where `coordinate_quality` is '99', those are
    addresses outside the US.
    """
    class Quality(DjangoChoices):
        # http://geoservices.tamu.edu/Services/Geocode/About/#NAACCRGISCoordinateQualityCodes
        AddressPoint = ChoiceItem('00',
            'Coordinates derived from local government-maintained address '
            'points, which are based on property parcel locations, not '
            'interpolation over a street segment’s address range')
        GPS = ChoiceItem('01',
            'Coordinates assigned by Global Positioning System (GPS)')
        Parcel = ChoiceItem('02', 'Coordinates are match of house number and '
            'street, and based on property parcel location')
        StreetSegmentInterpolation = ChoiceItem('03', 'Coordinates are match '
            'of house number and street, interpolated over the matching '
            'street segment’s address range')
        AddressZipCentroid = ChoiceItem('09',
            'Coordinates are address 5-digit ZIP code centroid')
        POBoxZIPCentroid = ChoiceItem('10', 'Coordinates are point ZIP code '
            'of Post Office Box or Rural Route')
        CityCentroid = ChoiceItem('11', 'Coordinates are centroid of address '
            'city (when address ZIP code is unknown or invalid, and there are '
            'multiple ZIP codes for the city)')
        Unknown = ChoiceItem('98', 'Latitude and longitude are assigned, but '
            'coordinate quality is unknown')
        Unmatchable = ChoiceItem('99', 'Latitude and longitude are not '
            'assigned, but geocoding was attempted; unable to assign '
            'coordinates based on available information')

    address1 = models.CharField(max_length=200, null=True, blank=True)
    # DEPRECATED
    address2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=75, null=True, blank=True)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=11, null=True, blank=True)
    coordinate = geo_models.PointField(null=True, blank=True)
    coordinate_quality = models.CharField(max_length=2, null=True, blank=True)
    canonical = models.ForeignKey('self', related_name='aliases',
        null=True, blank=True)

    # MANAGERS
    objects = geo_models.GeoManager()

    class Meta:
        ordering = ('address1', )
        unique_together = ('address1', 'city', 'state', 'zipcode')
        verbose_name_plural = 'addresses'

    def __unicode__(self):
        return self.get_display_name()

    def get_absolute_url(self):
        return reverse('tx_lobbying:address_detail', kwargs={'pk': self.pk})

    # CUSTOM PROPERTIES
    ###################

    @property
    def coordinate_quality_label(self):
        return self.Quality.values.get(self.coordinate_quality)

    @property
    def original_addresses(self):
        """
        The address as it was originally entered into registration reports.
        """
        def lob_addr(x):
            return '{ADDRESS1} {ADDRESS2}, {CITY}, {STATE} {ZIPCODE}'.format(**x)

        def comp_addr(compensation):
            return '{EC_ADR1} {EC_ADR2}, {EC_CITY}, {EC_STCD} {EC_ZIP4}'.format(**compensation)

        addresses_used = defaultdict(list)
        for item in self.registrationreport_set.all().select_related('lobbyist'):
            address = lob_addr(item.raw)
            addresses_used[address].append(item)
        for item in self.compensation_set.all().select_related('report__lobbyist'):
            address = comp_addr(item.raw)
            addresses_used[address].append(item.report)
        # XXX cast back to dict so Django templates don't freak out
        # https://code.djangoproject.com/ticket/16335
        return dict(addresses_used)

    # CUSTOM METHODS
    ################

    def as_adr(self, enclosing_tag='p'):
        """
        Get the address formatted in the h-adr microformat.

        http://microformats.org/wiki/h-adr
        """
        return mark_safe(get_template('tx_lobbying/includes/address_adr.html')
            .render(Context({'object': self})))

    def geocode(self):
        from .utils import geocode_address
        geocode_address(self)

    def get_display_name(self, sep=u' \n'):
        bits = []
        if self.address1:
            bits.append(self.address1)
        bits.append(u'{0.city}, {0.state} {0.zipcode}'.format(self))
        output = sep.join(bits)
        if output.strip() == u',':
            return 'none'
        return output


class Interest(models.Model):
    """A lobbying interest such as a corporation or organization."""
    name = models.CharField(max_length=200, unique=True)
    address = models.ForeignKey(Address)

    # denormalized data
    slug = models.SlugField(max_length=200, null=True, blank=True)  # not unique

    # USER FIELDS
    canonical = models.ForeignKey('self', related_name='aliases',
        null=True, blank=True)

    # THIRD-PARTY INTEGRATION
    # this id should be unique, but we don't care if it isn't
    nomenklatura_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.address.state)

    def get_absolute_url(self):
        return reverse('tx_lobbying:interest_detail', kwargs={
            'pk': self.pk,
            'slug': self.slug,
        })

    # CUSTOM PROPERTIES

    @property
    def compensation_set_massive(self):
        """Just like .compensation_set, but includes aliases too."""
        return Compensation.objects.filter(Q(interest=self) |
            Q(interest__in=self.aliases.all()))

    @property
    def address_set(self):
        return self.get_all_addresses()

    @property
    def address_set_massive(self):
        return self.get_all_addresses(include_aliases=True)

    @property
    def nomenklatura_url(self):
        if self.nomenklatura_id:
            return (u'http://opennames.org/entities/{}'
                .format(self.nomenklatura_id))
        return ''

    @property
    def nomenklatura_review_url(self):
        if self.nomenklatura_id:
            return (u'http://opennames.org/datasets/tx-lobbying-interests/review/{}'
                .format(self.nomenklatura_id))
        return ''

    # CUSTOM METHODS

    def make_stats_for_year(self, year):
        # WISHLIST move into utils
        qs = self.compensation_set_massive
        aggregate_stats = qs.filter(annum__year=year).aggregate(
            guess=Sum('amount_guess'),
            high=Sum('amount_high'),
            low=Sum('amount_low'),
            lobbyist_count=Count('pk'),
        )
        if not aggregate_stats['lobbyist_count']:
            return
        interest = self.canonical if self.canonical else self
        stat, __ = InterestStats.objects.update_or_create(
            interest=interest, year=year,
            defaults=aggregate_stats)
        return stat

    def make_stats(self):
        # This could be done a lot better, but works for now
        data_set = self.compensation_set_massive.select_related('annum')
        try:
            year_min = data_set.earliest('annum__year').annum.year
            year_max = data_set.latest('annum__year').annum.year
            for year in range(year_min, year_max + 1):
                self.make_stats_for_year(year)
            # grab latest address
            latest_address = (self.compensation_set
                .filter(address__isnull=False)
                .latest('annum__year').address)
            if self.address != latest_address:
                self.address = latest_address
                self.save()
        except Compensation.DoesNotExist:
            # don't care
            pass

    def get_all_addresses(self, include_aliases=False):
        if include_aliases:
            return Address.objects.filter(Q(compensation__interest=self) |
                Q(compensation__interest__in=self.aliases.all())).distinct()
        return Address.objects.filter(compensation__interest=self).distinct()


class InterestStats(models.Model):
    """Denormalized data about an `Interest` for a year."""
    interest = models.ForeignKey(Interest, related_name='stats')
    year = models.IntegerField(null=True, blank=True)
    guess = models.IntegerField(null=True, blank=True)
    high = models.IntegerField(null=True, blank=True)
    low = models.IntegerField(null=True, blank=True)
    lobbyist_count = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('interest', 'year')
        ordering = ('year', )

    def __unicode__(self):
        return (u"{0.interest} compensated {0.lobbyist_count} "
            "${0.low} - ${0.high} ({0.year})".format(self))


class Lobbyist(models.Model):
    """
    An individual registered with the TEC as a lobbyist.

    There are multiple name fields, and it may seem redundant, but many
    lobbyists are organizations, not people. Organizations do not have first and
    last names. The `sort_name` field is last, first for people, and just name
    for organizations. It is given to us by the TEC in the data.
    """
    filer_id = models.IntegerField(unique=True)
    updated_at = models.DateField()  # manually set by import scripts
    # name, max_length as defined by CSV schema
    name = models.CharField(max_length=100)
    sort_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=45)  # if lobbyist is a person
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=15)
    suffix = models.CharField(max_length=5)
    nick_name = models.CharField(max_length=25)
    address = models.ForeignKey(Address, null=True, blank=True)

    # denormalized data
    slug = models.SlugField(max_length=100, null=True, blank=True)  # not unique

    class Meta:
        ordering = ('sort_name', )

    def __unicode__(self):
        return Lobbyist.get_display_name(self.__dict__)

    def get_absolute_url(self):
        return reverse('tx_lobbying:lobbyist_detail', kwargs={
            'filer_id': self.filer_id,
            'slug': self.slug,
        })

    # CUSTOM METHODS

    @staticmethod
    def get_display_name(data):
        """
        Get how to display a `Lobbyist`'s name from a dict.

        This is a staticmethod and takes a dict so we can re-use this data on
        any arbitrary dict (or json) data.
        """
        if data['nick_name']:
            return u'%(first_name)s "%(nick_name)s" %(last_name)s' % data
        elif data['first_name']:
            return u'%(first_name)s %(last_name)s' % data
        return data['name']

    def get_name_history(self, unique=True):
        """Get a list of all the different names a `Lobbyist` has used."""
        from .scrapers.utils import get_name_data
        history = []
        for report in self.coversheets.exclude(raw=None):
            data = get_name_data(report.raw)
            name = Lobbyist.get_display_name(data)
            if (not unique or not history) or (history and name != history[-1][0]):
                history.append((name, report))
        return history

    def get_occupation_history(self, unique=True):
        """Get a list of all the different occupations listed."""
        history = []
        for report in self.registrations.exclude(raw=None):
            data = report.raw
            name = data['NORM_BUS']
            if (not unique or not history) or (history and name != history[-1][0]):
                history.append((name, report))
        return history

    def get_address_history(self):
        """Get a list of all the different addresses used."""
        # TODO get data off `RegistrationReport`, .registrations.all()

        history = []
        Item = namedtuple('Item', ['address', 'registration'])  # NOQA
        for reg in self.registrations.all().order_by('year'):
            address = reg.address
            if not history or address != history[-1].address:
                # only append address if it changed
                history.append(Item(address, reg))
        return history

    def make_stats(self):
        values = self.coversheets.values('year').annotate(
            Sum('transportation'),
            Sum('food'),
            Sum('entertainment'),
            Sum('gifts'),
            Sum('awards'),
            Sum('events'),
            Sum('media'),
            Sum('ben_senators'),
            Sum('ben_representatives'),
            Sum('ben_other'),
            Sum('ben_legislative'),
            Sum('ben_executive'),
            Sum('ben_family'),
            Sum('ben_events'),
            Sum('ben_guests'),
            Sum('total_spent'),
            Sum('total_benefited'),
            Sum('spent_guess'),
        )
        # group coversheets by year
        year_data = defaultdict(lambda: defaultdict(int))
        for data in values:
            year = data.pop('year')
            for k, v in data.iteritems():
                year_data[year][k[:-5]] += v
        # update stats
        for year, data in year_data.items():
            LobbyistStats.objects.update_or_create(lobbyist=self, year=year,
                defaults=data)


class LobbyistStats(models.Model):
    """
    Stats about a lobbyist derived from other models for a year.
    """
    lobbyist = models.ForeignKey(Lobbyist, related_name="stats")
    year = models.IntegerField()
    # `Coversheet` fields again
    # expenses
    transportation = models.DecimalField("Transportation & Lodging",
        max_digits=12, decimal_places=2, default='0.00')
    food = models.DecimalField("Food & Beverages",
        max_digits=12, decimal_places=2, default='0.00')
    entertainment = models.DecimalField("Entertainment",
        max_digits=12, decimal_places=2, default='0.00')
    gifts = models.DecimalField("Gifts",
        max_digits=12, decimal_places=2, default='0.00')
    awards = models.DecimalField("Awards & Memementos",
        max_digits=12, decimal_places=2, default='0.00')
    events = models.DecimalField("Political Fundraiers / Charity Events",
        max_digits=12, decimal_places=2, default='0.00')
    media = models.DecimalField("Mass Media Communications",
        max_digits=12, decimal_places=2, default='0.00')
    ben_senators = models.DecimalField("State Senators",
        max_digits=12, decimal_places=2, default='0.00')
    ben_representatives = models.DecimalField("State Representatives",
        max_digits=12, decimal_places=2, default='0.00')
    ben_other = models.DecimalField("Other Elected/Appointed Officials",
        max_digits=12, decimal_places=2, default='0.00')
    ben_legislative = models.DecimalField("Legislative Branch Employees",
        max_digits=12, decimal_places=2, default='0.00')
    ben_executive = models.DecimalField("Executive Agency Employees",
        max_digits=12, decimal_places=2, default='0.00')
    ben_family = models.DecimalField("Family of Legis/Exec Branch",
        max_digits=12, decimal_places=2, default='0.00')
    ben_events = models.DecimalField("Events - All Legis Invited",
        max_digits=12, decimal_places=2, default='0.00')
    ben_guests = models.DecimalField("Guests",
        max_digits=12, decimal_places=2, default='0.00')
    # derived fields
    total_spent = models.DecimalField(
        max_digits=13, decimal_places=2, default='0.00')
    total_benefited = models.DecimalField(
        max_digits=13, decimal_places=2, default='0.00')
    spent_guess = models.DecimalField(
        max_digits=13, decimal_places=2, default='0.00')

    class Meta:
        ordering = ('year', )
        unique_together = ('lobbyist', 'year')

    def __unicode__(self):
        return u'{0.lobbyist} spent ${0.total_spent} ({0.year})'.format(self)


class RegistrationReport(RawDataMixin, models.Model):
    """
    A reference to the registration report a `Lobbyist` files every year.

    This is the report where someone officially registers as a lobbyist. It
    also lists the clients they represent. These reports can be amended, so a
    registration from 2008 can be amended in 2013 and change on you.

    A report only has one `Lobbyist`, but can have many `Interest`s.
    """
    lobbyist = models.ForeignKey(Lobbyist, related_name="registrations")
    # REPNO
    report_id = models.IntegerField(unique=True)
    # RPT_DATE
    report_date = models.DateField()
    # YEAR_APPL
    year = models.IntegerField()
    address = models.ForeignKey(Address,
        help_text='The address the lobbyist listed for themself.')

    class Meta:
        ordering = ('year', 'report_date')

    def __unicode__(self):
        return u"%s %s %s" % (self.report_id, self.report_date, self.lobbyist)

    def get_absolute_url(self):
        return reverse('tx_lobbying:registration_detail', kwargs={
            'repno': self.report_id,
        })


class Coversheet(RawDataMixin, models.Model):
    """
    Cover sheet.

    Lobbyists have to file a cover sheet with all their expenses for the year
    (or month? or what?). This contains everything and is the root model for
    all expense reports.
    """
    lobbyist = models.ForeignKey(Lobbyist, related_name="coversheets")
    report_date = models.DateField()
    # REPNO
    report_id = models.PositiveIntegerField(unique=True)
    # CORR_NUM
    correction = models.PositiveSmallIntegerField(default=0,
        help_text='Correction Number (0=Original)')
    # YEAR_APPL
    year = models.PositiveSmallIntegerField()
    # expenses
    transportation = models.DecimalField("Transportation & Lodging",
        max_digits=12, decimal_places=2, default=0)
    food = models.DecimalField("Food & Beverages",
        max_digits=12, decimal_places=2, default=0)
    entertainment = models.DecimalField("Entertainment",
        max_digits=12, decimal_places=2, default=0)
    gifts = models.DecimalField("Gifts",
        max_digits=12, decimal_places=2, default=0)
    awards = models.DecimalField("Awards & Memementos",
        max_digits=12, decimal_places=2, default=0)
    events = models.DecimalField("Political Fundraiers / Charity Events",
        max_digits=12, decimal_places=2, default=0)
    media = models.DecimalField("Mass Media Communications",
        max_digits=12, decimal_places=2, default=0)
    ben_senators = models.DecimalField("State Senators",
        max_digits=12, decimal_places=2, default=0)
    ben_representatives = models.DecimalField("State Representatives",
        max_digits=12, decimal_places=2, default=0)
    ben_other = models.DecimalField("Other Elected/Appointed Officials",
        max_digits=12, decimal_places=2, default=0)
    ben_legislative = models.DecimalField("Legislative Branch Employees",
        max_digits=12, decimal_places=2, default=0)
    ben_executive = models.DecimalField("Executive Agency Employees",
        max_digits=12, decimal_places=2, default=0)
    ben_family = models.DecimalField("Family of Legis/Exec Branch",
        max_digits=12, decimal_places=2, default=0)
    ben_events = models.DecimalField("Events - All Legis Invited",
        max_digits=12, decimal_places=2, default=0)
    ben_guests = models.DecimalField("Guests",
        max_digits=12, decimal_places=2, default=0)
    # Schedule A
    subjects = models.ManyToManyField('Subject', related_name='reports')
    # derived fields
    total_spent = models.DecimalField(
        max_digits=13, decimal_places=2, default=0)
    total_benefited = models.DecimalField(
        max_digits=13, decimal_places=2, default=0)
    spent_guess = models.DecimalField(max_digits=13, decimal_places=2,
        default='0.00', help_text='max(total_spent, total_benefited)')

    class Meta:
        get_latest_by = 'year'
        ordering = ('report_date', )

    def __unicode__(self):
        return u'%s %s %s' % (self.report_id, self.report_date, self.lobbyist)

    def get_absolute_url(self):
        return reverse('tx_lobbying:coversheet_detail', kwargs={
            'filer_id': self.lobbyist.filer_id,
            'slug': self.lobbyist.slug,
            'report_id': self.report_id,
        })


class ExpenseDetailReport(RawDataMixin, models.Model):
    """
    Detailed expense report.

    If a lobbyist spends enough, they have to file a detailed expense report.
    This is not very useful data because there are a lot of loopholes so that
    lobbyists can get around having to file a detailed expense report.
    """
    # IDNO
    idno = models.PositiveIntegerField()
    # REPNO
    cover = models.ForeignKey(Coversheet, related_name="details")
    # FILER_ID
    lobbyist = models.ForeignKey(Lobbyist, related_name="expensedetails")
    # YEAR_APPL
    year = models.IntegerField()
    # EXPAMOUNT
    amount = models.DecimalField(max_digits=12, decimal_places=2,
        default=0, null=True)
    # other fields
    type = models.CharField(max_length=20)
    amount_guess = models.DecimalField(max_digits=12, decimal_places=2,
        default=0)

    class Meta:
        ordering = ('cover__report_date', )
        unique_together = ('idno', 'type')

    def __unicode__(self):
        return u"%s - %s ($%s)" % (self.cover, self.type, self.amount_guess)


# Fun data
class LobbyistAnnum(models.Model):
    """A report of a `Lobbyist`'s relationship to `Interest`s for a year."""
    lobbyist = models.ForeignKey(Lobbyist, related_name='years')
    year = models.IntegerField()
    clients = models.ManyToManyField(Interest, through='Compensation',
        related_name='years_available')

    class Meta:
        ordering = ('-year', )
        unique_together = ('lobbyist', 'year')

    def __unicode__(self):
        return u"%s (%s)" % (self.lobbyist, self.year)


class Compensation(RawDataMixin, models.Model):
    """
    Details about how a `Lobbyist` was compensated by an `Interest` for a year.

    Compensation ranges are very loosely defined, and are usually not
    indicative of the actual amount a `Lobbyist` was paid.

    This model also holds extra information about a the lobbyist's relationship
    from the registration form.

    The `amount_guess` field is a derived field that is the a guess of what the
    `Lobbyist` was actually paid. For now it is just the average of the upper
    and lower bound of pay ranges, but in the future more variables could be
    considered.
    """
    amount_high = models.IntegerField()  # upper bound, exlusive
    amount_low = models.IntegerField()  # lower bound, inclusive
    # TYPECOPM
    compensation_type = models.CharField(max_length=20, null=True, blank=True)
    # STARTDR
    start_date = models.DateField(null=True, blank=True)
    # TERMDATE
    end_date = models.DateField(null=True, blank=True)
    # RPT_DATE
    updated_at = models.DateField()
    # relationships to other models
    annum = models.ForeignKey(LobbyistAnnum)
    interest = models.ForeignKey(Interest)
    address = models.ForeignKey(Address, null=True, blank=True,
        help_text='The address the lobbyist listed for the `Interest`')
    # temporarily make nullable during data transition
    # CLIENT_NUM
    client_num = models.PositiveSmallIntegerField(null=True, blank=True,
        help_text='Client ID for lobbyist. The client number assigned to this '
        'client on the most recently filed registration.')
    # temporarily make nullable during data transition
    report = models.ForeignKey(RegistrationReport, null=True, blank=True)

    # denormalized fields
    amount_guess = models.IntegerField()  # denormalized, f(amount_low, amount_high)

    class Meta:
        ordering = ('interest__name', 'annum__year', 'annum__lobbyist', )
        unique_together = ('annum', 'interest')

    def __unicode__(self):
        # TODO, thousands separator... requires python 2.7
        return u"{1.interest} pays {0} ~${1.amount_guess} ({1.annum})".format(
            self.annum.lobbyist, self)


class Subject(models.Model):
    # CATGNUM
    category_id = models.PositiveIntegerField()
    # CATG_TEXT (aka CATG_DESC)
    description = models.CharField(max_length=50)
    # OTH_DESC, only used if CATGNUM == 84
    other_description = models.CharField(max_length=50, blank=True)

    name = models.CharField(max_length=50, null=True, blank=True,
        help_text=u'Human curated name')
    slug = models.SlugField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ('category_id', 'slug')

    def __unicode__(self):
        if self.name:
            return self.name
        return (self.other_description
            if self.category_id == 84 else self.description)

    def get_absolute_url(self):
        return reverse('tx_lobbying:subject_detail',
            kwargs={'slug': self.slug})
