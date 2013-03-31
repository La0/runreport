from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from club.views import *

urlpatterns = patterns('',
  url(r'^/?$', login_required(ClubMembers.as_view()), name="club"),

  # Member
  url(r'^(?P<username>[\w\_]+)/?', login_required(ClubMember.as_view()), name="club-member"),
)

