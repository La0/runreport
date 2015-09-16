from django.views.generic import FormView, DetailView
from django.http import HttpResponseRedirect
from sport.tasks import publish_report
from sport.forms import SportWeekPublish
from mixins import CurrentWeekMixin, WeekPaginator
from coach.mixins import JsonResponseMixin, JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD, JSON_OPTION_ONLY_AJAX, JSON_OPTION_REDIRECT_SKIP

class WeekPublish(JsonResponseMixin, CurrentWeekMixin, FormView):
  template_name = 'sport/week/publish.html'
  form_class = SportWeekPublish
  json_options = [JSON_OPTION_ONLY_AJAX, ]

  def get_context_data(self, *args, **kwargs):
    # FormView does not embed local object
    context = super(WeekPublish, self).get_context_data(*args, **kwargs)
    context['report'] = self.get_object()
    return context

  def form_valid(self, form):
    # Checks
    report = self.get_object()
    if self.request.user.demo:
      raise Exception("No publish in demo")
    if not report.is_publiable():
      raise Exception('Not publiable.')

    # Add a comment to conversation
    if form.cleaned_data['comment']:
      report.add_comment(form.cleaned_data['comment'], self.request.user)

    # Publish new report to all memberships
    uri = self.request.build_absolute_uri('/')[:-1] # remove trailing /
    for m in self.request.user.memberships.filter(role__in=('athlete', 'trainer')):
      task = publish_report.delay(report, m, uri)

    # Save last task id in report
    # Dirty: should save all tasks. But it's not really used anymore :(
    report.task = task.id
    report.save()

    # Reload parent
    if self.request.is_ajax():
      self.json_options = [JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD]
      return self.render_to_response({})

    # Transition to week view when not ajax
    self.json_options = [JSON_OPTION_REDIRECT_SKIP, ]
    return HttpResponseRedirect(report.get_absolute_url())

class WeeklyReport(CurrentWeekMixin, WeekPaginator, DetailView):
  template_name = 'sport/week/edit.html'
