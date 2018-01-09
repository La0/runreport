from django.conf.urls import patterns, url
from events.views import *

# Should be club's places patterns only
urlpatterns = patterns('',

                       # List club places
                       url(r'^/?$', PlaceList.as_view(), name="places"),

                       # Create a club place
                       url(r'^new/?$', PlaceCreate.as_view(), name="place-create"),

                       # Create a club place
                       url(r'^(?P<pk>\d+)/?$',
                           PlaceUpdate.as_view(),
                           name="place-edit"),
                       )
