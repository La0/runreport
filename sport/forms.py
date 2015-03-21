#- coding: utf-8
from models import Sport, SportDay, SportSession, SESSION_TYPES
from datetime import date
from django import forms
from django.utils.translation import ugettext_lazy as _
from sport.fields import IntervalWidget, IntervalFormField
from plan.models import PLAN_SESSION_APPLICATIONS

class SportSessionForm(forms.ModelForm):
  time = IntervalFormField(widget=IntervalWidget(attrs={'placeholder': 'hh:mm'}), required=False)
  distance = forms.FloatField(localize=True, widget=forms.TextInput(attrs={'placeholder': 'km'}), required=False)

  # Plan Session status
  plan_status = forms.ChoiceField(choices=PLAN_SESSION_APPLICATIONS, widget=forms.HiddenInput(), required=False)

  class Meta:
    model = SportSession
    fields = ('sport', 'distance', 'time', 'name', 'comment', 'type', 'race_category')
    widgets = {
      'sport' : forms.HiddenInput(),
      'type' : forms.HiddenInput(),
    }

  def __init__(self, default_sport=None, day_date=None, *args, **kwargs):
    self.day_date = day_date
    super(SportSessionForm, self).__init__(*args, **kwargs)

    # Load only sports of depth 1 for this form
    self.sports = Sport.objects.filter(depth=1)
    self.fields['sport'].queryset = self.sports

    # Apply default sport to instance
    if not hasattr(self.instance, 'sport'):
      self.instance.sport = default_sport

    # Apply initial value for PlanSession's status
    if hasattr(self.instance, 'plan_session'):
      self.fields['plan_status'].initial = self.instance.plan_session.status

  def clean_plan_status(self):
    status = self.cleaned_data.get('plan_status')

    # Check the status is not applied for past sessions
    if hasattr(self.instance, 'plan_session'):
      if not status:
        raise forms.ValidationError(_('You must select a status for your training plan.'))
      today = date.today()
      if today >= self.day_date and status == 'applied':
        raise forms.ValidationError(_('You must validate your training plan (select Done or Missed).'))

    return status


  def clean(self, *args, **kwargs):
    data = super(SportSessionForm, self).clean(*args, **kwargs)

    # No check for rest session
    if data['type'] == 'rest':
      return self.cleaned_data

    # Check we have time or distance for
    # * all trainings
    # * past sessions
    # * skip failed plans
    if ( \
        data['type'] == 'training' or \
        ( data['type'] == 'race' and self.day_date <= date.today() ) \
      ) \
      and data.get('plan_status') != 'failed' \
      and 'distance' in data and data['distance'] is None \
      and 'time' in data and data['time'] is None:
      raise forms.ValidationError(u'Spécifiez une distance ou un temps pour ajouter une séance.')

    # Alert user about missing comment & name
    if not self.cleaned_data.get('name', None) and not self.cleaned_data.get('comment', None):
      raise forms.ValidationError(u'Vous devez spécifier un nom de séance et/ou un commentaire.')

    # Only for race
    if data['type'] == 'race':

      # Check time & distance are set, for past races
      #session_date = self.instance.date or self.prefix # Get the date even if not in db
      #if session_date <= date.today() and (self.cleaned_data.get('time', None) is None or self.cleaned_data.get('distance', None) is None):
      #  raise forms.ValidationError(u"Pour une course passée, renseignez la distance et le temps.")

      # Check race category
      if not data['race_category']:
        raise forms.ValidationError(u"Sélectionnez un type de course.")

    return self.cleaned_data

class SportDayAddForm(forms.Form):
  '''
  Form to create manually a new empty session
  '''
  date = forms.DateField()
  type = forms.ChoiceField(required=False, choices=SESSION_TYPES)

  def __init__(self, user, *args, **kwargs):
    self.user = user
    super(SportDayAddForm, self).__init__(*args, **kwargs)

  def clean_date(self):

    # Check date is free
    if SportDay.objects.filter(week__user=self.user, date=self.cleaned_data['date']):
      raise forms.ValidationError('Une séance existe déjà à cette date.')

    return self.cleaned_data['date']

class SportWeekPublish(forms.Form):
  '''
  Add a comment while publising a week
  '''
  comment = forms.CharField(required=False, widget=forms.Textarea())
