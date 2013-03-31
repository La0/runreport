from django.conf.urls import patterns, include, url
from club.views import *

urlpatterns = patterns('',
  url(r'^/?$', ClubMembers.as_view(), name="club"),

  # Member
  url(r'^(?P<username>[\w\_]+)/?', ClubMember.as_view(), name="club-member"),
)

