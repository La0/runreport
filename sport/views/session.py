from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django.views.generic import DateDetailView
from sport.forms import SportSessionForm
from sport.models import SportSession
from coach.mixins import JsonResponseMixin, JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE
from mixins import CalendarDay
from django.core.urlresolvers import reverse

class SportSessionAdd(CalendarDay, JsonResponseMixin, ModelFormMixin, ProcessFormView, DateDetailView):
  model = SportSession
  form_class = SportSessionForm
  template_name = 'sport/session.html'

  def get_form_kwargs(self, *args, **kwargs):
    self.get_object() # Load day

    # Init a session
    self.session = SportSession(sport=self.request.user.default_sport, day=self.object)

    return {
      'instance' : self.session,
      'multi_sports' : self.request.user.multi_sports,
      'default_sport' : self.request.user.default_sport,
      'data' : self.request.method == 'POST' and self.request.POST or None,
    }

  def get_context_data(self, *args, **kwargs):
    context = super(SportSessionAdd, self).get_context_data(*args, **kwargs)
    context['session'] = self.session
    return context

  def form_valid(self, form):

    # Save session, but create day before
    session = form.save(commit=False)
    if not self.object.pk:
      self.object.save()
    session.day = self.object
    session.save()

    # Configure output
    self.json_options = [JSON_OPTION_NO_HTML, JSON_OPTION_CLOSE]
    self.json_boxes = {
      'day-%s' % self.day : reverse('report-day-edit', args=[self.day.year, self.day.month, self.day.day]),
    }

    return self.render_to_response({})
