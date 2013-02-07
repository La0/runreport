from coffin.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^login/$', 'users.views.login', name='login'),
  url(r'^logout/$', 'users.views.logout', name='logout'),
)
