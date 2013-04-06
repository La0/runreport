from django.conf.urls import patterns, url
from club.views import *

urlpatterns = patterns('',
  # Members, with week view
  url(r'^/?$', ClubMembers.as_view(), name="club-current"),
  url(r'^week/(?P<year>\d{4})/(?P<week>\d{1,2})/?$', ClubMembers.as_view(), name="club-week"),

  # Member
  url(r'^(?P<username>[\w\_]+)/?', ClubMember.as_view(), name="club-member"),
)

