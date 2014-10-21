from django.views.generic.detail import DetailView, BaseDetailView
from mixins import TrackMixin
from coach.mixins import JsonResponseMixin, JSON_OPTION_RAW

class TrackView(TrackMixin, DetailView):
  template_name = 'tracks/view.html'

class TrackCoordsView(TrackMixin, JsonResponseMixin, BaseDetailView):
  json_options = [JSON_OPTION_RAW, ]

  def get_context_data(self, *args, **kwargs):
    track = self.object
    return {
      # Base informations
      'id' : track.id,
      'provider' : {
        'name' : track.provider,
        'id' : track.provider_id,
      },

      # Output the coordinates
      'coordinates' : track.simple.coords,
    }
