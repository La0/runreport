from coffin.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
  url(r'^login/?$', 'users.views.login', name='login'),
  url(r'^profile/?$', 'users.views.profile', name='user-profile'),
  url(r'^garmin/?$', 'users.views.garmin', name='user-garmin'),
  url(r'^create/?$', CreateUser.as_view(), name='user-create'),
  url(r'^logout/?$', 'users.views.logout', name='logout'),
)
