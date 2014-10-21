from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from tracks.views import *

urlpatterns = patterns('',

  # Oauth redirection
  url(r'^oauth/(?P<provider>\w+)/?', login_required(TrackOauthRedirect.as_view()), name="track-oauth"),

  # Ger track coordinates
  url(r'^coords/(?P<track_id>\d+).json$', TrackCoordsView.as_view(), name="track-coords"),

  # View a track
  url(r'^(?P<track_id>\d+)/?', TrackView.as_view(), name="track-view"),
)

