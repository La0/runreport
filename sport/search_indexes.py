from haystack import indexes
from sport.models import SportSession


class SportSesionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr='name', document=True, use_template=True)

    def get_model(self):
        return SportSession

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        """
        return self.get_model().objects.all()
