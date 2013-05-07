from django.views.generic import WeekArchiveView
from helpers import week_to_date
from run.models import RunReport
from datetime import datetime
from run.forms import RunReportForm, RunSessionForm
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
    self.sessions = self.report.get_dated_sessions()

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

  def get_form_report(self):

    form = None, None
    if not self.report.published:
      if self.request.method == 'POST':
        form = RunReportForm(self.request.POST, instance=self.report)
      else:
        form = RunReportForm(instance=self.report)

    return form

  def get_dated_forms(self):
    '''
    Build a form per day and per RunSession instance
    Much more easier than dealing with a dynamic model formset
    '''
    forms = {}
    for day in self.report.get_days():
      instance = self.sessions[day]
      if self.request.method == 'POST':
        f = RunSessionForm(self.request.POST, instance=instance, prefix=day)
      else:
        f = RunSessionForm(instance=instance, prefix=day)
      forms[day] = f

    return forms

  def get_context_data(self, **kwargs):
    context = super(WeeklyReport, self).get_context_data(**kwargs)

    # Full context
    profile = self.request.user.get_profile()
    context.update({
      'forms' : self.get_dated_forms(),
      'form_report' : self.get_form_report(),
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
    if not self.report.published:

      # Save form per form, to only create necessary objects
      for day, form in context['forms'].items():
        if form.is_valid():
          session = form.save(commit=False)
          session.report = self.report
          session.date = day
          session.save()

      # Save report
      if context['form_report'].is_valid():
        context['form_report'].save()

      # Publish ?
      if request.POST['action'] == 'publish':
        self.report.publish()
    return self.render_to_response(context)