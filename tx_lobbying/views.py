from django.db.models import Count, Sum
from django.views.generic import DetailView, ListView, TemplateView

from .models import (Lobbyist, LobbyistStat,
    ExpenseCoversheet, ExpenseDetailReport)


class Landing(TemplateView):
    template_name = "tx_lobbying/landing.html"
    years = range(2005, 2014)

    def aggregate_covers(self):
        facets = ['transportation', 'food', 'entertainment', 'gifts', 'awards', 'events', 'media']
        data = dict()
        for year in self.years:
            qs = ExpenseCoversheet.objects.filter(year=year)
            year_data = qs.aggregate(*map(Sum, facets))
            year_data['total'] = sum(year_data.values())
            year_data['count'] = qs.count()
            year_data['itemized'] = qs.exclude(details__isnull=True).count()
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

    def get_context_data(self, **kwargs):
        context = super(YearLanding, self).get_context_data(**kwargs)
        year = kwargs['year']
        qs = LobbyistStat.objects.filter(year=year).order_by('-spent')[:20]
        context['object_list'] = qs
        return context


class LobbyistList(ListView):
    queryset = Lobbyist.objects.all().order_by('sort_name').\
        annotate(spent=Sum('coversheets__spent_guess')).\
        filter(spent__gt=0)


class LobbyistDetail(DetailView):
    queryset = Lobbyist.objects.all()
    slug_field = 'filer_id'
