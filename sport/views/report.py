from django.views.generic import WeekArchiveView
from helpers import week_to_date, check_task
from sport.models import SportWeek, SportSession, Sport, SESSION_TYPES
from datetime import datetime
from sport.forms import SportWeekForm, SportSessionForm
from sport.tasks import publish_report
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from mixins import WeekPaginator, CurrentWeekMixin, SportSessionForms

class WeeklyReport(SportSessionForms, CurrentWeekMixin, WeekArchiveView, WeekPaginator):
  template_name = 'sport/week/base.html'
  week_format = '%W'
  date_field = 'date'
  report = None

  def get_report(self):
    if self.week is not None:
      return self.week

    # Init week 
    self.week, _ = SportWeek.objects.get_or_create(user=self.request.user, year=self.get_year(), week=self.get_week())

    # Init days 
    self.days = self.week.get_days_per_date()

    return self.week

  def get_dated_items(self):
    # Init dates
    year = self.get_year()
    week = self.get_week()
    self.date = week_to_date(year, week)
    self.check_limits()

    # Init report & sessions
    self.week = self.get_report()

    context = {
      'report' : self.week,
      'now' : datetime.now(),
    }
    return ([], self.days, context)

  def get_form_report(self):

    form = None, None
    if not self.week.published:
      if self.request.method == 'POST':
        form = SportWeekForm(self.request.POST, instance=self.week)
      else:
        form = SportWeekForm(instance=self.week)

    return form

  def get_dated_forms(self):
    '''
    Build a form per session and per SportSession instance
    Sorted by days
    Much more easier than dealing with a dynamic model formset
    '''
    forms = {}
    for day_date in self.week.get_dates():
      forms[day_date] = self.get_sessions_forms(day_date, self.days[day_date])

    return forms

  def get_context_data(self, **kwargs):
    context = super(WeeklyReport, self).get_context_data(**kwargs)

    # Check the task on report
    check_task(self.week)

    # Full context
    context.update({
      'forms' : self.get_dated_forms(),
      'form_report' : self.get_form_report(),
      'report' : self.week,
      'now' : datetime.now(),
      'memberships' : self.request.user.memberships.all(),
      'sessions': self.days,
      'pagename' : 'report-week',
      'session_types':SESSION_TYPES,
    })

    # Pagination
    context.update(self.paginate(self.date, self.min_date, self.max_date))

    # Get previous report if not published
    report_previous = None
    if self.week.is_current() and context['week_previous']:
      try:
        report_previous = SportWeek.objects.get(user=self.request.user, year=context['week_previous']['year'], week=context['week_previous']['week'], published=False)
      except:
        pass
    context['report_previous'] = report_previous

    return context

  def get(self, request, *args, **kwargs):
    # Render minimal response
    if not request.user.is_authenticated():
      self.object_list = []
      self.template_name = "landing/index.html" # Use landing page
      return self.render_to_response({})
    return super(WeeklyReport, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    if not request.user.is_authenticated():
      raise PermissionDenied

    self.date_list, self.object_list, extra_context = self.get_dated_items()
    context = self.get_context_data(**{'object_list': self.object_list})

    # No post when published
    if self.week.published:
      return HttpResponseRedirect(self.week.get_absolute_url())

    # Save report
    form_report = context['form_report']
    if form_report.is_valid():
      form_report.save()

    # Publish through a celery task ?
    if 'publish' in request.POST and self.week.is_publiable():
      member = self.request.user.memberships.get(club__pk=int(request.POST['publish']))
      uri = self.request.build_absolute_uri('/')[:-1] # remove trailing /
      task = publish_report.delay(self.week, member, uri)

      # Save task id in report
      self.week.task = task.id
      self.week.save()

    # Redirect to lose POST on valid action
    if redirect:
      return HttpResponseRedirect(self.week.get_absolute_url())
    return self.render_to_response(context)

