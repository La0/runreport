from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^run/', include('run.urls')),
  url(r'^user/', include('users.urls')),

  url(r'^admin/', include(admin.site.urls)),
)
