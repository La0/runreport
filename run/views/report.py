from django.views.generic import WeekArchiveView
from helpers import week_to_date, date_to_day
from run.models import RunReport
from datetime import date, datetime
from run.forms import RunSessionFormSet, RunReportForm
from coach.settings import REPORT_START_DATE
from django.http import Http404
from django.core.exceptions import PermissionDenied
from mixins import WeekPaginator

class WeeklyReport(WeekArchiveView, WeekPaginator):
  template_name = 'run/index.html'
  week_format = '%W'
  date_field = 'date'
  report = None

  def get_year(self):
    year = datetime.now().year
    return int(self.kwargs.get('year', year))

  def get_week(self):
    week = datetime.now().strftime(self.week_format)
    return int(self.kwargs.get('week', week))

  def check_limits(self):
    # Load min & max date
    min_year, min_week = REPORT_START_DATE
    self.min_date = week_to_date(min_year, min_week)
    self.max_date = date_to_day(self.today)

    # Check we are not in past or future
    if self.date < self.min_date:
      raise Http404('Too old.')
    if self.date > self.today:
      raise Http404('In the future.')

  def get_report(self):
    if self.report is not None:
      return self.report

    # Init report
    self.report, created = RunReport.objects.get_or_create(user=self.request.user, year=self.get_year(), week=self.get_week())
    if created:
      self.report.init_sessions()
    return self.report


  def get_dated_items(self):
    # Init dates
    year = self.get_year()
    week = self.get_week()
    self.date = week_to_date(year, week)
    self.today = date.today()
    self.check_limits()

    # Init report & sessions
    self.report = self.get_report()
    profile = self.request.user.get_profile()
    self.sessions = self.report.sessions.all().order_by('date')

    context = {
      'trainer' : profile.trainer,
      'report' : self.report,
      'now' : datetime.now(),
      'profile' : profile,
    }
    return ([], self.sessions, context)

  def get_context_data(self, **kwargs):
    context = super(WeeklyReport, self).get_context_data(**kwargs)

    # Init forms
    form, form_report = None, None
    if not self.report.published:
      if self.request.method == 'POST':
        form = RunSessionFormSet(self.request.POST)
        form_report = RunReportForm(self.request.POST, instance=self.report)
      else:
        form = RunSessionFormSet(queryset=self.sessions)
        form_report = RunReportForm(instance=self.report)

    # Full context
    profile = self.request.user.get_profile()
    context.update({
      'form' : form,
      'form_report' : form_report,
      'report' : self.report,
      'now' : datetime.now(),
      'trainer' : profile.trainer,
      'profile' : profile,
      'sessions': self.sessions,
    })

    # Pagination
    context.update(self.paginate(self.date, self.min_date, self.max_date))

    # Get previous report if not published
    report_previous = None
    if self.report.is_current() and context['week_previous']:
      try:
        report_previous = RunReport.objects.get(user=self.request.user, week=context['week_previous']['week'], published=False)
      except:
        pass
    context['report_previous'] = report_previous

    return context

  def get(self, request, *args, **kwargs):
    # Render minimal response
    if not request.user.is_authenticated():
      self.object_list = []
      return self.render_to_response({})
    return super(WeeklyReport, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied
    self.date_list, self.object_list, extra_context = self.get_dated_items()
    context = self.get_context_data(**{'object_list': self.object_list})
    self.report = self.get_report()
    if not self.report.published:
      if context['form'].is_valid():
        context['form'].save()

      # Sace report
      if context['form_report'].is_valid():
        context['form_report'].save()

      # Publish ?
      if request.POST['action'] == 'publish':
        self.report.publish()
    return self.render_to_response(context)
