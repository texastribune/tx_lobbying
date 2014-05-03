from collections import namedtuple
import json

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count, Sum, Q


class Address(models.Model):
    """An address"""
    address1 = models.CharField(max_length=200, null=True, blank=True)
    address2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=75, null=True, blank=True)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=11, null=True, blank=True)
    # latitude
    # longitude

    class Meta:
        ordering = ('address1', )

    def __unicode__(self):
        bits = []
        if self.address1:
            bits.append(self.address1)
        if self.address2:
            bits.append(self.address2)
        bits.append(u'{0.city}, {0.state} {0.zipcode}'.format(self))
        output = u' \n'.join(bits)
        if output.strip() == u',':
            return 'none'
        return output

    def get_absolute_url(self):
        return reverse('tx_lobbying:address_detail', kwargs={'pk': self.pk})


class Interest(models.Model):
    """A lobbying interest such as a corporation or organization."""
    name = models.CharField(max_length=200, unique=True)
    address = models.ForeignKey(Address)

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
        return reverse('tx_lobbying:interest_detail', kwargs={'pk': self.pk})

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
        year_min = self.years_available.earliest('year').year
        year_max = self.years_available.latest('year').year
        for year in range(year_min, year_max + 1):
            self.make_stats_for_year(year)

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
    # NORM_BUS
    # TODO business = models.CharField(max_length=100)

    class Meta:
        ordering = ('sort_name', )

    def __unicode__(self):
        return Lobbyist.get_display_name(self.__dict__)

    def get_absolute_url(self):
        return reverse('tx_lobbying:lobbyist_detail', kwargs=dict(slug=self.filer_id))

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
        for report in self.coversheets.exclude(raw=''):
            data = get_name_data(json.loads(report.raw))
            name = Lobbyist.get_display_name(data)
            if (not unique or not history) or (history and name != history[-1][0]):
                history.append((name, report))
        return history

    def get_address_history(self):
        """Get a list of all the different addresses used."""
        # TODO get data off `RegistrationReport`, .registrations.all()

        history = []
        Item = namedtuple('Item', ['address', 'registration'])
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
        for data in values:
            year = data.pop('year')
            defaults = {k[:-5]: v for k, v in data.items()}
            LobbyistStats.objects.update_or_create(lobbyist=self, year=year,
                defaults=defaults)


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
        return u"{0.lobbyist} spent ${0.spent:,.2f} ({0.year})".format(self)


class RegistrationReport(models.Model):
    """
    A reference to the registration report a `Lobbyist` files every year.

    This is the report where someone officially registers as a lobbyist. It
    also lists the clients they represent. These reports can be amended, so a
    registration from 2008 can be ammended in 2013 and change on you.

    A report only has one `Lobbyist`, but can have many `Interest`s.
    """
    lobbyist = models.ForeignKey(Lobbyist, related_name="registrations")
    report_id = models.IntegerField(unique=True)
    report_date = models.DateField()
    year = models.IntegerField()
    address = models.ForeignKey(Address)
    raw = models.TextField()
    # TODO
    # interests = models.ManyToMany(Interest)

    class Meta:
        ordering = ('year', )

    def __unicode__(self):
        return u"%s %s %s" % (self.report_id, self.report_date, self.lobbyist)


class Coversheet(models.Model):
    """
    Cover sheet.

    Lobbyists have to file a cover sheet with all their expenses for the year
    (or month? or what?). This contains everything.
    """
    lobbyist = models.ForeignKey(Lobbyist, related_name="coversheets")
    raw = models.TextField()
    report_date = models.DateField()
    report_id = models.IntegerField(unique=True)
    year = models.IntegerField()
    # expenses
    transportation = models.DecimalField("Transportation & Lodging",
        max_digits=12, decimal_places=2, default="0.00")
    food = models.DecimalField("Food & Beverages",
        max_digits=12, decimal_places=2, default="0.00")
    entertainment = models.DecimalField("Entertainment",
        max_digits=12, decimal_places=2, default="0.00")
    gifts = models.DecimalField("Gifts", max_digits=12, decimal_places=2, default="0.00")
    awards = models.DecimalField("Awards & Memementos",
        max_digits=12, decimal_places=2, default="0.00")
    events = models.DecimalField("Political Fundraiers / Charity Events",
        max_digits=12, decimal_places=2, default="0.00")
    media = models.DecimalField("Mass Media Communications",
        max_digits=12, decimal_places=2, default="0.00")
    ben_senators = models.DecimalField("State Senators",
        max_digits=12, decimal_places=2, default="0.00")
    ben_representatives = models.DecimalField("State Representatives",
        max_digits=12, decimal_places=2, default="0.00")
    ben_other = models.DecimalField("Other Elected/Appointed Officials",
        max_digits=12, decimal_places=2, default="0.00")
    ben_legislative = models.DecimalField("Legislative Branch Employees",
        max_digits=12, decimal_places=2, default="0.00")
    ben_executive = models.DecimalField("Executive Agency Employees",
        max_digits=12, decimal_places=2, default="0.00")
    ben_family = models.DecimalField("Family of Legis/Exec Branch",
        max_digits=12, decimal_places=2, default="0.00")
    ben_events = models.DecimalField("Events - All Legis Invited",
        max_digits=12, decimal_places=2, default="0.00")
    ben_guests = models.DecimalField("Guests",
        max_digits=12, decimal_places=2, default="0.00")
    # derived fields
    total_spent = models.DecimalField(max_digits=13, decimal_places=2, default="0.00")
    total_benefited = models.DecimalField(max_digits=13, decimal_places=2, default="0.00")
    spent_guess = models.DecimalField(max_digits=13, decimal_places=2,
        default='0.00', help_text='max(total_spent, total_benefited)')

    class Meta:
        ordering = ('report_date', )

    def __unicode__(self):
        return u"%s %s %s" % (self.report_id, self.report_date, self.lobbyist)


class ExpenseDetailReport(models.Model):
    """
    Detailed expense report.

    If a lobbyist spends enough, they have to file a detailed expense report.
    This is not very useful data because there are a lot of loopholes so that
    lobbyists can get around having to file a detailed expense report.
    """
    # IDNO
    idno = models.IntegerField()
    # REPNO
    cover = models.ForeignKey(Coversheet, related_name="details")
    # FILER_ID
    lobbyist = models.ForeignKey(Lobbyist, related_name="expensedetails")
    # YEAR_APPL
    year = models.IntegerField()
    # EXPAMOUNT
    amount = models.DecimalField(max_digits=12, decimal_places=2,
        default="0.00", null=True)
    # other fields
    type = models.CharField(max_length=20)
    amount_guess = models.DecimalField(max_digits=12, decimal_places=2,
        default="0.00")
    raw = models.TextField()

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


class Compensation(models.Model):
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
    annum = models.ForeignKey(LobbyistAnnum)
    interest = models.ForeignKey(Interest)
    address = models.ForeignKey(Address, null=True, blank=True,
        help_text='The address the lobbyist listed for the `Interest`')
    raw = models.TextField()
    updated_at = models.DateField()

    # denormalized fields
    amount_guess = models.IntegerField()  # denormalized, f(amount_low, amount_high)

    class Meta:
        ordering = ('interest__name', 'annum__year', 'annum__lobbyist', )
        unique_together = ('annum', 'interest')

    def __unicode__(self):
        # TODO, thousands separator... requires python 2.7
        return u"{1.interest} pays {0} ~${1.amount_guess} ({1.annum})".format(
            self.annum.lobbyist, self)

    # CUSTOM PROPERTIES

    @property
    def raw_data(self):
        return json.loads(self.raw)
