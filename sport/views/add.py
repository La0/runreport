from django.views.generic.edit import FormView
from sport.forms import SportDayAddForm
from sport.models import SportWeek, SportDay
from helpers import date_to_week
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from coach.mixins import JsonResponseMixin, JSON_OPTION_REDIRECT_SKIP

class SessionAdd(JsonResponseMixin, FormView):
  type_asked = False
  form_class = SportDayAddForm
  template_name = 'sport/add.html'

  def get_context_data(self, *args, **kwargs):
    context = super(SessionAdd, self).get_context_data(*args, **kwargs)
    context['type_asked'] = self.type_asked
    context['source_url'] = self.request.path
    return context

  def get_form_kwargs(self, *args, **kwargs):
    context = super(SessionAdd, self).get_form_kwargs(*args, **kwargs)
    context['user'] = self.request.user

    # Lookup asked type
    if 'type' in self.kwargs:
      context['initial']['type'] = self.kwargs['type']
      self.type_asked = True

    return context

  def form_valid(self, form):
    # Get (or create) week report
    week, year = date_to_week(form.cleaned_data['date'])
    report, _ = SportWeek.objects.get_or_create(user=self.request.user, year=year, week=week)

    # Create a new session
    session_type = form.cleaned_data['type'] or self.kwargs.get('type', 'training')
    self.session = SportDay.objects.create(report=report, date=form.cleaned_data['date'], type=session_type)

    return super(SessionAdd, self).form_valid(form)

  def get_success_url(self):
    # Display created session
    self.json_options = [JSON_OPTION_REDIRECT_SKIP, ]
    url = reverse('report-day', args=(self.session.date.year, self.session.date.month, self.session.date.day))
    return url
