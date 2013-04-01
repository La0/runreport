from coffin.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
  url(r'^login/?$', LoginUser.as_view(), name='login'),
  url(r'^profile/?$', 'users.views.profile', name='user-profile'),
  url(r'^garmin/?$', 'users.views.garmin', name='user-garmin'),
  url(r'^create/?$', CreateUser.as_view(), name='user-create'),
  url(r'^logout/?$', LogoutUser.as_view(), name='logout'),
)
