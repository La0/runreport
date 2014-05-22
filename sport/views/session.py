from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django.views.generic import DateDetailView
from sport.forms import SportSessionForm
from sport.models import SportSession
from coach.mixins import JsonResponseMixin
from mixins import CalendarDay

class SportSessionAdd(CalendarDay, JsonResponseMixin, ModelFormMixin, ProcessFormView, DateDetailView):
  model = SportSession
  form_class = SportSessionForm
  template_name = 'sport/session.html'

  def get_form_kwargs(self, *args, **kwargs):
    self.get_object() # Load day

    # TODO in mixin
    self.session = SportSession(sport=self.request.user.default_sport)

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


