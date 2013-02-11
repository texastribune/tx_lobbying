from django.views.generic import DetailView, ListView

from .models import Lobbyist


class LobbyistList(ListView):
    queryset = Lobbyist.objects.all().order_by('sort_name')


class LobbyistDetail(DetailView):
    queryset = Lobbyist.objects.all()
    slug_field = 'filer_id'
