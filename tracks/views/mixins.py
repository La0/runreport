from tracks.models import Track
from django.shortcuts import get_object_or_404

class TrackMixin(object):
  '''
  Load a track and check user
  can access it
  '''
  model = Track
  context_object_name = 'track'

  def get_object(self):
    # TODO: use get_user & rights
    return get_object_or_404(Track, pk=self.kwargs['track_id'], session__day__week__user=self.request.user)
