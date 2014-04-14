from run.forms import RunSessionForm
from coach.mixins import JsonResponseMixin, JSON_STATUS_ERROR
from django.views.generic import DateDetailView
from django.views.generic.edit import ModelFormMixin, ProcessFormView, DeleteView
from mixins import CalendarDay
from django.core.urlresolvers import reverse

class RunCalendarDay(CalendarDay, JsonResponseMixin, ModelFormMixin, ProcessFormView, DateDetailView):
  template_name = 'run/day.html'
  form_class = RunSessionForm

  def get_form(self, form_class):
    # Load object before form init
    if not hasattr(self, 'object'):
      self.get_object()
    return super(RunCalendarDay, self).get_form(form_class)

  def form_valid(self, form):
    form.save()
    return self.render_to_response(self.get_context_data(**{'form' : form, 'saved': True}))

  def form_invalid(self, form):
    self.json_status = JSON_STATUS_ERROR
    return self.render_to_response(self.get_context_data(**{'form' : form}))

class RunCalendarDayDelete(CalendarDay, JsonResponseMixin, DeleteView, DateDetailView):
  template_name = 'run/day_delete.html'

  def get_success_url(self):
    return reverse('report-month', args=(self.day.year, self.day.month))
