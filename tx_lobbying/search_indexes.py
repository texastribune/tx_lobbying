"""
Haystack search indicies.

I denormalize thing here to try and make things easier on the database later.
"""
from haystack import indexes

from .models import Lobbyist, Interest


class LobbyistIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr='name', document=True)
    content_auto = indexes.EdgeNgramField(model_attr='name')
    url = indexes.CharField()

    def get_model(self):
        return Lobbyist

    def get_updated_field(self):
        return 'updated_at'

    def prepare_url(self, obj):
        return obj.get_absolute_url()


class InterestIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr='name', document=True)
    content_auto = indexes.EdgeNgramField(model_attr='name')
    url = indexes.CharField()

    def get_model(self):
        return Interest

    def prepare_url(self, obj):
        return obj.get_absolute_url()
