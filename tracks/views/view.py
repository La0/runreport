from django.views.generic import DetailView
from tracks.models import Track
from django.shortcuts import get_object_or_404

class TrackView(DetailView):
  template_name = 'tracks/view.html'
  context_object_name = 'track'

  def get_object(self):
    return get_object_or_404(Track, pk=self.kwargs['track_id'], session__day__week__user=self.request.user)
