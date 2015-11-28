from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from sport.views import *

day_patterns = patterns('',

  # Modal View
  url(r'^/?$', login_required(RunCalendarDay.as_view()), name="report-day"),

  # Delete
  url(r'^/delete/?$', login_required(RunCalendarDayDelete.as_view()), name="report-day-delete"),

  # Session management
  url(r'^/session/add$', login_required(SportSessionView.as_view()), name="sport-session-add"),
  url(r'^/session/(?P<session>\d+)/edit$', login_required(SportSessionView.as_view()), name="sport-session-edit"),
  url(r'^/session/(?P<session>\d+)/delete$', login_required(SportSessionDelete.as_view()), name="sport-session-delete"),

)


urlpatterns = patterns('',
  # Dashboard
  url(r'^/?$', DashBoardView.as_view(), name="dashboard"),
  url(r'^(?P<type>athlete|trainer)/?$', DashBoardView.as_view(), name="dashboard-type"),
  url(r'^trainer/(?P<club>[\w_\-]+)/?$', DashBoardView.as_view(), name="dashboard-club"),
  url(r'^demo/skip/?$', DemoSkipView.as_view(), name='demo-skip'),

  # Week / Report
  url(r'^week/?$', WeeklyReport.as_view(), name="report-current"),
  url(r'^week/(?P<year>\d{4})/(?P<week>\d{1,2})/publish/?$', WeekPublish.as_view(), name="report-week-publish"),
  url(r'^week/(?P<year>\d{4})/(?P<week>\d{1,2})/?$', WeeklyReport.as_view(), name="report-week"),

  # Calendar month
  url(r'^calendar/?$', login_required(RunCalendar.as_view()), name="report-current-month"),
  url(r'^calendar/(?P<year>\d{4})/(?P<month>\d{1,2})/?$', login_required(RunCalendar.as_view()), name="report-month"),

  # Day
  url(r'^calendar/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})', include(day_patterns)),

  # Calendar year
  url(r'^calendar/(?P<year>\d{4})/?$', login_required(RunCalendarYear.as_view()), name="report-year"),

  # Export a month
  url(r'^export/(?P<year>\d{4})/(?P<month>\d{1,2})/?$', login_required(ExportMonth.as_view()), name="export-month"),

  # Vma
  url(r'^vma/glossaire/?', VmaGlossary.as_view(), name="vma-glossary"),
  url(r'^vma/?', login_required(VmaPaces.as_view()), name="vma"),

  # Stats
  url(r'^stats/?$', login_required(SportStats.as_view()), name='stats'),
  url(r'^stats/all/?$', login_required(SportStats.as_view()), name='stats-all', kwargs={'all': True}),
  url(r'^stats/(?P<year>\d{4})/?$', login_required(SportStats.as_view()), name='stats-year'),
)
