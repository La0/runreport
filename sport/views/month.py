from django.views.generic import MonthArchiveView, DateDetailView, View
from django.views.generic.dates import MonthMixin, YearMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django.http import Http404
from sport.models import SportSession, SportDay, SportWeek, SESSION_TYPES
from datetime import datetime, date
import calendar
import collections
from coach.mixins import JsonResponseMixin, JSON_STATUS_ERROR, CsvResponseMixin
from helpers import date_to_week

class RunCalendar(MonthArchiveView):
  template_name = 'sport/calendar/month.html'
  date_field = 'date'
  model = SportDay
  context_object_name = 'sessions'
  allow_future = True
  allow_empty = True

  def get_year(self):
    year = datetime.now().year
    return int(self.kwargs.get('year', year))

  def get_month(self):
    month = datetime.now().month
    return int(self.kwargs.get('month', month))

  def get_user(self):
    return self.request.user

  def get_links(self):
    return {
      'pageargs' : [],
      'pageyear' : 'report-year',
      'pagemonth' : 'report-month',
      'pageday' : 'report-day',
    }

  # Load all days & weeks for this month
  def load_calendar(self, year, month):
    cal = calendar.Calendar(calendar.MONDAY)
    self.days = [d for d in cal.itermonthdates(year, month)]
    self.weeks = cal.monthdatescalendar(year, month)

  def get_dated_items(self):
    year = self.get_year()
    month = self.get_month()
    date = datetime.strptime('%s %s 1' % (year, month), '%Y %m %d')
    try:
      self.load_calendar(year, month)
    except Exception, e:
      raise Http404(str(e))

    # Load all sessions for this month
    sessions = SportDay.objects.filter(week__user=self.get_user(), date__in=self.days)
    sessions_per_days = dict((r.date, r) for r in sessions)
    sessions_per_days = collections.OrderedDict(sorted(sessions_per_days.items()))

    context = {
      'months' : (self.get_previous_month(date), date, self.get_next_month(date)),
      'days' : self.days,
      'weeks' : self.weeks,
    }
    context.update(self.get_links())
    return (self.days, sessions_per_days, context)

class ExportMonth(CsvResponseMixin, MonthMixin, YearMixin, View):
  '''
  Export a month sessions, in CSV format
  '''
  def get(self, *args, **kwargs):
    # Get year and month
    month = int(self.get_month())
    year = int(self.get_year())

    # Load calendar
    try:
      cal = calendar.Calendar(calendar.MONDAY)
      days = [d for d in cal.itermonthdates(year, month) if d.month == month]
    except:
      raise Http404('Invalid export date.')

    # Load sessions
    day_format = '%A %d %B %Y'
    data = []
    sessions = SportSession.objects.filter(day__week__user=self.request.user, day__date__in=days)
    for day in days:
      day_sessions = sessions.filter(day__date=day)
      if day_sessions.count() > 0:

        # Serialize every session as a list, for csv render
        for session in day_sessions.all():
          data.append([
            day.strftime(day_format),
            session.type,
            session.name.encode('utf-8'),
            session.comment.encode('utf-8'),
            session.distance,
            session.time,
          ])
      else:
        # Just display empty day
        data.append([ day.strftime(day_format), ])

    # Build csv lines
    context = {
      'csv_filename' : '%s_%d_%d' % (self.request.user.username, year, month),
      'csv_data' : data,
    }
    return self.render_to_response(context)
