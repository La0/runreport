from django.conf.urls import patterns, url
from badges.views import *

urlpatterns = patterns('',
  url(r'^/?$', BadgesView.as_view(), name="badges"),
)
