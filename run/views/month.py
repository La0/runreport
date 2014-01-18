from django.views.generic import MonthArchiveView, DateDetailView, View
from django.views.generic.dates import MonthMixin, YearMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django.http import Http404
from run.models import RunSession, RunReport, SESSION_TYPES
from run.forms import RunSessionForm
from datetime import datetime, date
import calendar
from coach.mixins import JsonResponseMixin, JSON_STATUS_ERROR, CsvResponseMixin
from helpers import date_to_week

class RunCalendar(MonthArchiveView):
  template_name = 'run/month.html'
  date_field = 'date'
  model = RunSession
  context_object_name = 'sessions'
  allow_future = True
  allow_empty = True

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
      'pageargs' : [],
      'pagemonth' : 'report-month',
      'pageday' : 'report-day',
    }
    return (self.days, sessions_per_days, context)

class RunCalendarDay(JsonResponseMixin, ModelFormMixin, ProcessFormView, DateDetailView):
  template_name = 'run/day.html'
  month_format = '%M'
  context_object_name = 'session'
  form_class = RunSessionForm

  def get_form(self, form_class):
    # Load object before form init
    if not hasattr(self, 'object'):
      self.get_object()
    return super(RunCalendarDay, self).get_form(form_class)

  def form_valid(self, form):
    form.save()
    return self.render_to_response(self.get_context_data(**{'form' : form}))

  def form_invalid(self, form):
    self.json_status = JSON_STATUS_ERROR
    return self.render_to_response(self.get_context_data(**{'form' : form}))

  def get_context_data(self, **kwargs):
    context = super(RunCalendarDay, self).get_context_data(**kwargs)
    context['day'] = self.day
    context['report'] = self.report
    context['session_types'] = SESSION_TYPES
    return context

  def get_object(self):
    # Load day, report and eventual session
    self.day = date(int(self.get_year()), int(self.get_month()), int(self.get_day()))
    week, year = date_to_week(self.day)
    self.report, _ = RunReport.objects.get_or_create(user=self.request.user, year=year, week=week)
    try:
      self.object = RunSession.objects.get(report=self.report, date=self.day)
    except:
      self.object = RunSession(report=self.report, date=self.day)
    return self.object

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
      days = [d for d in cal.itermonthdates(year, month)]
    except:
      raise Http404('Invalid export date.')

    # Load sessions
    data = []
    sessions = RunSession.objects.filter(report__user=self.request.user, date__in=days)
    for day in days:
      if day.month != month:
        continue # Skip before & after days

      day_data = [ day.strftime('%A %d %B %Y'), ]
      try:
        session = sessions.get(date=day)

        # Serialize a session as a list, for csv render
        day_data += [
          session.type,
          session.name.encode('utf-8'),
          session.comment.encode('utf-8'),
          session.distance,
          session.time,
        ]
      except:
        pass
      data.append(day_data)

    # Build csv lines
    context = {
      'csv_filename' : '%s_%d_%d' % (self.request.user.username, year, month),
      'csv_data' : data,
    }
    return self.render_to_response(context)
