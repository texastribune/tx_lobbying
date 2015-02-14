from haystack import indexes

from .models import Lobbyist, Interest


class LobbyistIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr='name', document=True)

    def get_model(self):
        return Lobbyist

    def get_updated_field(self):
        return 'updated_at'


class InterestIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr='name', document=True)

    def get_model(self):
        return Interest
