from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
  url(r'^/?$', 'run.views.index', name="report-current"),
)
