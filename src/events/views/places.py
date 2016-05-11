from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from club.views.mixins import ClubMixin
from .mixins import PlaceClubMixin

class PlaceList(ClubMixin, ListView):
  template_name = 'events/places/index.html'
  context_object_name = 'places'

  def get_queryset(self):
    return self.club.places.all()

class PlaceCreate(PlaceClubMixin, CreateView):
  pass

class PlaceUpdate(PlaceClubMixin, UpdateView):
  pass
