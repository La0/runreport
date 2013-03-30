from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from run.views import *

urlpatterns = patterns('',
  url(r'^/?$', 'run.views.report', name="report-current"),
  url(r'^week/(?P<year>\d{4})/(?P<week>\d{1,2})/?$', 'run.views.report', name="report-week"),
  url(r'^(?P<year>\d{4})/(?P<week>\d{2})/excel$', 'run.views.excel', name="report-excel"),

  # Calendar
  url(r'^calendar/?$', login_required(RunCalendar.as_view()), name="report-current-month"),
  url(r'^calendar/(?P<year>\d{4})/(?P<month>\d{1,2})/?$', login_required(RunCalendar.as_view()), name="report-month"),

  # Vma
  url(r'^vma/glossaire/?', VmaGlossary.as_view(), name="vma-glossary"),
  url(r'^vma/?', login_required(VmaPaces.as_view()), name="vma"),
)
