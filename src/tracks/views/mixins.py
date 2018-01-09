from tracks.models import Track
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied


class TrackMixin(object):
    '''
    Load a track and check user
    can access it
    '''
    model = Track
    context_object_name = 'track'

    def get_object(self, check_ownership=False):
        # Load requested track
        self.track = get_object_or_404(Track, pk=self.kwargs['track_id'])

        # Check right access to tracks
        track_user = self.track.session.day.week.user
        if check_ownership and track_user != self.request.user:
            raise PermissionDenied
        if 'tracks' not in track_user.get_privacy_rights(self.request.user):
            raise PermissionDenied

        return self.track
