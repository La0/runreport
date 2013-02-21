from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
  url(r'^/?$', 'run.views.report', name="report-current"),
  url(r'^week/(?P<year>\d{4})/(?P<week>\d{1,2})/?$', 'run.views.report', name="report-week"),
  url(r'^(?P<year>\d{4})/(?P<week>\d{2})/excel$', 'run.views.excel', name="report-excel"),

  # Calendar
  url(r'^calendar/?$', 'run.views.month', name="report-current-month"),
  url(r'^calendar/(?P<year>\d{4})/(?P<month>\d{1,2})/?$', 'run.views.month', name="report-month"),
)
