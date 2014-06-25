from django.views.generic.edit import ModelFormMixin, ProcessFormView, DeleteView
from django.views.generic import DateDetailView
from sport.forms import SportSessionForm
from coach.mixins import JsonResponseMixin, JSON_OPTION_BODY_RELOAD, JSON_OPTION_NO_HTML
from mixins import CalendarSession
from django.core.urlresolvers import reverse
from datetime import datetime

class SportSessionView(CalendarSession, JsonResponseMixin, ModelFormMixin, ProcessFormView, DateDetailView):
  form_class = SportSessionForm
  template_name = 'sport/session/edit.html'

  def get_form_kwargs(self, *args, **kwargs):
    self.get_object() # Load day & session
    return {
      'instance' : self.session,
      'default_sport' : self.request.user.default_sport,
      'data' : self.request.method == 'POST' and self.request.POST or None,
      'day_date' : self.day,
    }

  def get_context_data(self, extra=None, *args, **kwargs):
    context = super(SportSessionView, self).get_context_data(*args, **kwargs)
    context['now'] = datetime.now()

    # Url for edit or add ?
    args = [self.day.year, self.day.month, self.day.day]
    base = 'sport-session-add'
    if self.session.pk:
      args += [self.session.pk, ]
      base = 'sport-session-edit'
    context['form_url'] = reverse(base, args=args)

    # Override form data
    if extra:
      context.update(extra)

    # Modal from form ?
    context['modal'] = 'modal' in self.request.POST

    return context

  def form_valid(self, form):

    # Save session, but create day before
    session = form.save(commit=False)
    if not self.object.pk:
      self.object.save()
    session.day = self.object
    session.save()

    # Render as saved
    context = self.get_context_data(extra={'form' : form, 'saved' : True})
    return self.render_to_response(context)

class SportSessionDelete(CalendarSession, JsonResponseMixin, DeleteView, DateDetailView):
  template_name = 'sport/session/delete.html'

  def delete(self, *args, **kwargs):
    '''
    Delete session, then reload
    '''
    self.get_object()
    self.session.delete()

    # Configure output to reload page
    self.json_options = [JSON_OPTION_NO_HTML, JSON_OPTION_BODY_RELOAD]

    return self.render_to_response({})
