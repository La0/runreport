from sport.forms import SportSessionForm
from sport.models import SportDay
from coach.mixins import JsonResponseMixin, JSON_STATUS_ERROR
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

  def get_success_url(self):
    return reverse('report-month', args=(self.day.year, self.day.month))

