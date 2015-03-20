from django.views.generic import UpdateView, DetailView
from sport.tasks import publish_report
from mixins import CurrentWeekMixin, WeekPaginator
from coach.mixins import JsonResponseMixin, JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD

class WeekPublish(JsonResponseMixin, CurrentWeekMixin, UpdateView):
  template_name = 'sport/week/publish.html'
  form_class = None # TODO !!!

  def form_valid(self, form):
    # Checks
    if self.request.user.demo:
      raise Exception("No publish in demo")
    if not self.object.is_publiable():
      raise Exception('Not publiable.')

    # Publish new report to all memberships
    report = form.save()
    uri = self.request.build_absolute_uri('/')[:-1] # remove trailing /
    for m in self.request.user.memberships.all():
      task = publish_report.delay(report, m, uri)

    # Save last task id in report
    # Dirty: should save all tasks. But it's not really used anymore :(
    report.task = task.id
    report.save()

    # Reload parent
    self.json_options = [JSON_OPTION_CLOSE, JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD]
    return self.render_to_response({})

class WeeklyReport(CurrentWeekMixin, WeekPaginator, DetailView):
  template_name = 'sport/week/edit.html'

  def get(self, request, *args, **kwargs):
    # Render minimal response
    # for visitors
    if not request.user.is_authenticated():
      self.object_list = []
      self.template_name = "landing/index.html" # Use landing page
      return self.render_to_response({})

    return super(WeeklyReport, self).get(request, *args, **kwargs)

