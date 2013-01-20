import json

from django.db import models


class Interest(models.Model):
    """A lobbying interest such as a corporation or organization."""
    name = models.CharField(max_length=200)
    state = models.CharField(max_length=2)

    class Meta:
        unique_together = ('name', 'state')

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.state)

    def make_stats_for_year(self, year):
        # TODO move into utils
        guess = 0
        high = 0
        low = 0
        count = 0
        # TODO refactor
        for compensation in self.compensation_set.filter(year__year=year):
            guess += compensation.amount_guess
            high += compensation.amount_high
            low += compensation.amount_low
            count += 1
        stat, __ = InterestStats.objects.get_or_create(interest=self, year=year)
        stat.guess = guess
        stat.high = high
        stat.low = low
        stat.lobbyist_count = count
        stat.save()
        return stat


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

    def __unicode__(self):
        return (u"{0.interest} compensated {0.lobbyist_count} "
            "${0.low} - ${0.high} ({0.year})".format(self))


class Lobbyist(models.Model):
    """An individual registered with the TEC as a lobbyist."""
    filer_id = models.IntegerField(unique=True)
    sort_name = models.CharField(max_length=150)
    updated_at = models.DateField()  # manually set by import scripts
    # name, max_length as defined by CSV schema
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=15)
    suffix = models.CharField(max_length=5)
    nick_name = models.CharField(max_length=25)

    def __unicode__(self):
        return Lobbyist.get_display_name(self.__dict__)

    @staticmethod
    def get_display_name(data):
        if data['nick_name']:
            return u'%(first_name)s "%(nick_name)s" %(last_name)s' % data
        elif data['first_name']:
            return u'%(first_name)s %(last_name)s' % data
        return data['sort_name']

    def get_name_history(self, unique=True):
        from .scrapers.utils import get_name_data
        history = []
        for report in self.coversheet_set.exclude(raw=''):
            data = get_name_data(json.loads(report.raw))
            name = Lobbyist.get_display_name(data)
            if (not unique or not history) or (history and name != history[-1][0]):
                history.append((name, report))
        return history


class RegistrationReport(models.Model):
    """
    A reference to the registration report a `Lobbyist` files every year.

    This is the report where someone officially registers as a lobbyist. It also
    lists the clients they represent. These reports can be ammended, so a
    registration from 2008 can be ammended in 2013 and change on you.

    TODO: clients...

    """
    filer = models.ForeignKey(Lobbyist)
    raw = models.TextField()
    report_date = models.DateField()
    report_id = models.IntegerField(unique=True)
    year = models.IntegerField()

    def __unicode__(self):
        return u"%s %s %s" % (self.filer, self.report_date, self.report_id)


class Coversheet(models.Model):
    """
    Cover sheet.
    """
    lobbyist = models.ForeignKey(Lobbyist)
    raw = models.TextField()
    report_date = models.DateField()
    report_id = models.IntegerField(unique=True)
    year = models.IntegerField()

    class Meta:
        ordering = ('report_date', )

    def __unicode__(self):
        return u"%s %s %s" % (self.report_id, self.report_date, self.lobbyist)


# Fun data
class LobbyistYear(models.Model):
    """The list of `Interest`s a `Lobbyist` has for a year."""
    lobbyist = models.ForeignKey(Lobbyist, related_name='years')
    year = models.IntegerField()
    clients = models.ManyToManyField(Interest, through='Compensation',
        related_name='years_available')
    # expenses

    class Meta:
        ordering = ('-year', )
        unique_together = ('lobbyist', 'year')

    def __unicode__(self):
        return u"%s (%s)" % (self.lobbyist, self.year)


class Compensation(models.Model):
    """
    Details about how a `Lobbyist` was compensated by an `Interest` for a year.

    Compensation ranges are very loosely defined, and are usually not indicative
    of the actual amount a `Lobbyist` was paid.

    The `amount_guess` field is a derived field that is the a guess of what
    the `Lobbyist` was actually paid. For now it is just the average of the
    upper and lower bound of pay ranges, but in the future more variables could
    be considered.

    """
    amount_guess = models.IntegerField()  # denormalized, f(amount_low, amount_high)
    amount_high = models.IntegerField()  # upper bound, exlusive
    amount_low = models.IntegerField()  # lower bound, inclusive
    # compensation type
    # start
    # end
    year = models.ForeignKey(LobbyistYear)
    interest = models.ForeignKey(Interest)
    raw = models.TextField()
    updated_at = models.DateField()

    class Meta:
        # ordering = ('interest__name', )
        unique_together = ('year', 'interest')

    def __unicode__(self):
        # TODO, thousands separator... requires python 2.7
        return u"{1.interest} pays {0} ~${1.amount_guess} ({1.year})".format(
            self.year.lobbyist, self)
