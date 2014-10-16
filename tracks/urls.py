from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from tracks.views import *

urlpatterns = patterns('',

  # View a track
  url(r'^(?P<track_id>\d+)/?', login_required(TrackView.as_view()), name="track-view"),
)

