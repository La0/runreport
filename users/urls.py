from coffin.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^login/?$', 'users.views.login', name='login'),
  url(r'^profile/?$', 'users.views.profile', name='user-profile'),
  url(r'^create/?$', 'users.views.create', name='user-create'),
  url(r'^logout/?$', 'users.views.logout', name='logout'),
)
