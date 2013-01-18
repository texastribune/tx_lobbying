from django.db import models


class Interest(models.Model):
    name = models.CharField(max_length=200)
    state = models.CharField(max_length=2)

    class Meta:
        unique_together = ('name', 'state')

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.state)


class Lobbyist(models.Model):
    filer_id = models.IntegerField(unique=True)
    sort_name = models.CharField(max_length=150)
    updated_at = models.DateField()
    # name

    def __unicode__(self):
        return self.sort_name


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


# Fun data
class ClientList(models.Model):
    lobbyist = models.ForeignKey(Lobbyist)
    year = models.IntegerField()
    clients = models.ManyToManyField(Interest, through='Compensation')

    class Meta:
        ordering = ('-year', )
        unique_together = ('lobbyist', 'year')

    def __unicode__(self):
        return u"%s (%s)" % (self.lobbyist, self.year)


class Compensation(models.Model):
    amount_guess = models.IntegerField()  # denormalized, f(amount_low, amount_high)
    amount_high = models.IntegerField()  # upper bound, exlusive
    amount_low = models.IntegerField()  # lower bound, inclusive
    clientlist = models.ForeignKey(ClientList)
    interest = models.ForeignKey(Interest)
    raw = models.TextField()
    updated_at = models.DateField()

    class Meta:
        # ordering = ('interest__name', )
        unique_together = ('clientlist', 'interest')

    def __unicode__(self):
        # TODO, thousands separator... requires python 2.7
        return u"{1} pays {0} ~${2}".format(self.clientlist.lobbyist,
            self.interest, self.amount_guess)
