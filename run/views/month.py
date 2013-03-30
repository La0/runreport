from django.views.generic import MonthArchiveView
from django.http import Http404
from run.models import RunSession
from datetime import datetime
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
      'sessions_active' : sessions.exclude(comment=None,name=None),
      'months' : (self.get_previous_month(date), date, self.get_next_month(date)),
      'days' : self.days,
      'weeks' : self.weeks,
    }
    return (self.days, sessions_per_days, context)
