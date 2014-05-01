from django.db.models import Count, Sum
from django.views.generic import DetailView, ListView, TemplateView

from .models import (Lobbyist, ExpenseCoversheet, ExpenseDetailReport)
from . import models


class Landing(TemplateView):
    template_name = "tx_lobbying/landing.html"
    years = range(2005, 2015)

    def aggregate_covers(self):
        facets = ['transportation', 'food', 'entertainment', 'gifts', 'awards', 'events', 'media']
        data = dict()
        for year in self.years:
            qs = ExpenseCoversheet.objects.filter(year=year)
            year_data = qs.aggregate(*map(Sum, facets))
            try:
                year_data['total'] = sum(year_data.values())
            except TypeError:
                # no coversheets for that year
                continue
            year_data['count'] = qs.count()
            year_data['itemized'] = qs.exclude(details__isnull=True).count()
            year_data['registered'] = Lobbyist.objects.filter(
                registrations__year__exact=year).distinct().count()
            year_data['spent_anything'] = Lobbyist.objects.filter(
                stats__year__exact=year, stats__spent__gt=0).distinct().count()
            data[year] = year_data
        return data

    def aggregate_details(self):
        facets = ['food', 'entertainment', 'gift', 'award']
        data = dict()
        for year in self.years:
            qs = ExpenseDetailReport.objects.filter(year=year)
            year_data = {}
            total = 0
            count = 0
            for facet in facets:
                year_data[facet] = qs.filter(type=facet).\
                    aggregate(sum=Sum('amount_guess'), count=Count('amount_guess'))
                total += year_data[facet]['sum'] or 0
                count += year_data[facet]['count'] or 0
            year_data['total'] = total
            year_data['count'] = count  # same as qs.count()
            data[year] = year_data
        return data

    def get_context_data(self, **kwargs):
        context = super(Landing, self).get_context_data(**kwargs)
        context['covers'] = self.aggregate_covers()
        context['itemized'] = self.aggregate_details()
        return context


class YearLanding(TemplateView):
    template_name = "tx_lobbying/year_landing.html"

    def get_top_lobbyists(self, count=20):
        qs = (models.LobbyistStat.objects.filter(year=self.year)
            .select_related('lobbyist')
            .order_by('-spent')[:count])
        return qs

    def get_top_interests(self, count=20):
        qs = (models.InterestStats.objects
            .filter(year=self.year, interest__canonical__isnull=True)
            .select_related('interest')
            .order_by('-high')[:count])
        return qs

    def get_context_data(self, **kwargs):
        self.year = kwargs['year']
        context = super(YearLanding, self).get_context_data(**kwargs)
        context['top_lobbyists'] = self.get_top_lobbyists()
        context['top_interests'] = self.get_top_interests()
        return context


class LobbyistList(ListView):
    queryset = Lobbyist.objects.all().order_by('sort_name').\
        annotate(spent=Sum('coversheets__spent_guess')).\
        filter(spent__gt=0)


class LobbyistDetail(DetailView):
    queryset = Lobbyist.objects.all().prefetch_related(
        'years__compensation_set__interest', 'coversheets__details')
    slug_field = 'filer_id'


class InterestList(ListView):
    queryset = models.Interest.objects.all().select_related('canonical')


class InterestDetail(DetailView):
    model = models.Interest

    def get_context_data(self, **kwargs):
        data = super(InterestDetail, self).get_context_data(**kwargs)
        data['aliases'] = (self.object.aliases.all())
        data['compensation_set'] = (self.object.compensation_set_massive
            .prefetch_related('interest', 'year__lobbyist')
            .order_by('year__lobbyist', 'year__year'))
        return data
