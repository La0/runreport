from django.views.generic import WeekArchiveView
from django.forms.models import modelformset_factory
from helpers import week_to_date
from run.models import RunReport, RunSession
from datetime import datetime
from run.forms import RunReportForm
from django.core.exceptions import PermissionDenied
from mixins import WeekPaginator, CurrentWeekMixin

class WeeklyReport(CurrentWeekMixin, WeekArchiveView, WeekPaginator):
  template_name = 'run/index.html'
  week_format = '%W'
  date_field = 'date'
  report = None

  def get_report(self):
    if self.report is not None:
      return self.report

    # Init report
    self.report, _ = RunReport.objects.get_or_create(user=self.request.user, year=self.get_year(), week=self.get_week())

    # Init sessions
    self.sessions = self.report.sessions.all().order_by('date')

    # Missing days
    self.missing_days = []
    for day in self.report.get_days():
      try:
        self.sessions.get(date=day)
      except Exception:
        self.missing_days.append(day)

    return self.report

  def get_dated_items(self):
    # Init dates
    year = self.get_year()
    week = self.get_week()
    self.date = week_to_date(year, week)
    self.check_limits()

    # Init report & sessions
    self.report = self.get_report()
    profile = self.request.user.get_profile()

    context = {
      'trainer' : profile.trainer,
      'report' : self.report,
      'now' : datetime.now(),
      'profile' : profile,
    }
    return ([], self.sessions, context)

  def get_context_data(self, **kwargs):
    context = super(WeeklyReport, self).get_context_data(**kwargs)

    # Init formset
    RunSessionFormSet = modelformset_factory(RunSession, fields=('comment', 'name'), extra=len(self.missing_days), max_num=7)

    # Init forms
    form, form_report = None, None
    if not self.report.published:
      if self.request.method == 'POST':
        form = RunSessionFormSet(self.request.POST)
        form_report = RunReportForm(self.request.POST, instance=self.report)
      else:
        form = RunSessionFormSet(queryset=self.sessions)
        form_report = RunReportForm(instance=self.report)

      # Apply date & report to empty instances
      days = self.missing_days
      for f in form.forms:
        if f.instance.pk is None:
          f.instance.report = self.report
          f.instance.date = days.pop()

      # Finally sort forms by their date
      form.forms = sorted(form.forms, key=lambda f: f.instance.date)

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
      'pagename' : 'report-week',
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

      # Save report
      if context['form_report'].is_valid():
        context['form_report'].save()

      # Publish ?
      if request.POST['action'] == 'publish':
        self.report.publish()
    return self.render_to_response(context)
