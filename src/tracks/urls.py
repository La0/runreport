from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from tracks.views import *

urlpatterns = patterns('',

                       # Track providers user settings
                       url(r'^providers/?$',
                           login_required(TrackProviders.as_view()),
                           name="track-providers"),
                       url(r'^provider/(?P<name>\w+)/disconnect/?$',
                           login_required(TrackProviderDisconnect.as_view()),
                           name="track-provider-disconnect"),

                       # Oauth redirection
                       url(r'^oauth/(?P<provider>\w+)/?',
                           login_required(TrackOauthRedirect.as_view()),
                           name="track-oauth"),

                       # Get track coordinates
                       url(r'^coords/(?P<track_id>\d+).json$',
                           TrackCoordsView.as_view(), name="track-coords"),

                       # Update session
                       url(r'^session/(?P<track_id>\d+)/?',
                           TrackSessionView.as_view(),
                           name="track-session"),
                       )
