from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from run.views import *

urlpatterns = patterns('',
  url(r'^/?$', WeeklyReport.as_view(), name="report-current"),
  url(r'^week/(?P<year>\d{4})/(?P<week>\d{1,2})/?$', WeeklyReport.as_view(), name="report-week"),

  # Add a session
  url(r'^add/(?P<type>\w+)/?', login_required(SessionAdd.as_view()), name="session-add-type"),
  url(r'^add/?', login_required(SessionAdd.as_view()), name="session-add"),

  # Calendar month
  url(r'^calendar/?$', login_required(RunCalendar.as_view()), name="report-current-month"),
  url(r'^calendar/(?P<year>\d{4})/(?P<month>\d{1,2})/?$', login_required(RunCalendar.as_view()), name="report-month"),
  url(r'^calendar/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/?$', login_required(RunCalendarDay.as_view()), name="report-day"),
  url(r'^calendar/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/delete/?$', login_required(RunCalendarDayDelete.as_view()), name="report-day-delete"),

  # Calendar year
  url(r'^calendar/(?P<year>\d{4})/?$', login_required(RunCalendarYear.as_view()), name="report-year"),

  # Export a month
  url(r'^export/(?P<year>\d{4})/(?P<month>\d{1,2})/?$', login_required(ExportMonth.as_view()), name="export-month"),

  # Vma
  url(r'^vma/glossaire/?', VmaGlossary.as_view(), name="vma-glossary"),
  url(r'^vma/?', login_required(VmaPaces.as_view()), name="vma"),
)
