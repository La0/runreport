from sport.forms import SportSessionForm
from sport.models import SportDay
from coach.mixins import JsonResponseMixin, JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD
from .mixins import SportSessionForms
from django.views.generic import DateDetailView
from django.views.generic.edit import DeleteView
from mixins import CalendarDay
from django.core.urlresolvers import reverse
from datetime import datetime

class RunCalendarDay(SportSessionForms, CalendarDay, JsonResponseMixin, DateDetailView):
  template_name = 'sport/day/modal.html'

  def get_context_data(self, *args, **kwargs):
    context = super(RunCalendarDay, self).get_context_data(*args, **kwargs)
    context['now'] = datetime.now()
    context['forms'] = self.get_sessions_forms(self.day, self.object)
    return context

class RunCalendarDayDelete(CalendarDay, JsonResponseMixin, DeleteView, DateDetailView):
  template_name = 'sport/day/delete.html'

  def delete(self, *args, **kwargs):
    '''
    Delete day, then reload
    '''
    self.get_object()
    self.object.delete()
    self.object.rebuild_cache()

    # Configure output to reload page
    self.json_options = [JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD]
    return self.render_to_response({})
