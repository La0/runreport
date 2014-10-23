from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from tracks.views import *

urlpatterns = patterns('',

  # Oauth redirection
  url(r'^oauth/(?P<provider>\w+)/?', login_required(TrackOauthRedirect.as_view()), name="track-oauth"),

  # Get track coordinates
  url(r'^coords/(?P<track_id>\d+).json$', TrackCoordsView.as_view(), name="track-coords"),
)

