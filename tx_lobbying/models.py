from django.db import models


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
