from django.views.generic.edit import ModelFormMixin, ProcessFormView, DeleteView
from django.views.generic import DateDetailView
from sport.forms import SportSessionForm
from coach.mixins import JsonResponseMixin
from mixins import CalendarSession
from django.core.urlresolvers import reverse

class SportSessionView(CalendarSession, JsonResponseMixin, ModelFormMixin, ProcessFormView, DateDetailView):
  form_class = SportSessionForm
  template_name = 'sport/session.html'

  def get_form_kwargs(self, *args, **kwargs):
    self.get_object() # Load day & session

    return {
      'instance' : self.session,
      'multi_sports' : self.request.user.multi_sports,
      'default_sport' : self.request.user.default_sport,
      'data' : self.request.method == 'POST' and self.request.POST or None,
    }

  def get_context_data(self, *args, **kwargs):
    context = super(SportSessionView, self).get_context_data(*args, **kwargs)

    # Url for edit or add ?
    args = [self.day.year, self.day.month, self.day.day]
    base = 'sport-session-add'
    if self.session.pk:
      args += [self.session.pk, ]
      base = 'sport-session-edit'
    context['form_url'] = reverse(base, args=args)

    return context

  def form_valid(self, form):

    # Save session, but create day before
    session = form.save(commit=False)
    if not self.object.pk:
      self.object.save()
    session.day = self.object
    session.save()

    # Configure output
    self.reload_box()

    return self.render_to_response({})

class SportSessionDelete(CalendarSession, JsonResponseMixin, DeleteView, DateDetailView):
  template_name = 'sport/session.delete.html'

  def delete(self, *args, **kwargs):
    '''
    Delete session, then reload parent box
    '''
    self.get_object()
    self.session.delete()
    self.reload_box()
    return self.render_to_response({})
