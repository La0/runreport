from django.conf.urls import patterns, url
from gear.views import *

urlpatterns = patterns('',

  # Create a new gear
  url(r'^create/?$', GearCreateView.as_view(), name="gear-create"),

  # Manage a user gear
  url(r'^/?$', GearListView.as_view(), name="gear"),
  url(r'^(?P<pk>\d+)/edit/?$', GearEditView.as_view(), name="gear-edit"),
  url(r'^(?P<pk>\d+)/delete/?$', GearDeleteView.as_view(), name="gear-delete"),
)
