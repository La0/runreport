from django.views.generic import MonthArchiveView, DateDetailView
from django.http import Http404
from run.models import RunSession
from datetime import datetime, date
import calendar

class RunCalendar(MonthArchiveView):
  template_name = 'run/month.html'
  date_field = 'date'
  model = RunSession
  context_object_name = 'sessions'

  def get_year(self):
    year = datetime.now().year
    return int(self.kwargs.get('year', year))

  def get_month(self):
    month = datetime.now().month
    return int(self.kwargs.get('month', month))

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
    sessions = RunSession.objects.filter(report__user=self.request.user, date__in=self.days)
    sessions_per_days = dict((r.date, r) for r in sessions)

    context = {
      'months' : (self.get_previous_month(date), date, self.get_next_month(date)),
      'days' : self.days,
      'weeks' : self.weeks,
    }
    return (self.days, sessions_per_days, context)

class RunCalendarDay(DateDetailView):
  template_name = 'run/day.html'
  month_format = '%M'
  context_object_name = 'session'

  def get_object(self):
    self.date = date(int(self.get_year()), int(self.get_month()), int(self.get_day()))
    return RunSession.objects.get(report__user=self.request.user, date=self.date)
