#- coding: utf-8
from models import Sport, SportWeek, SportDay, SportSession, SESSION_TYPES
from datetime import date
from django import forms
from django.forms.models import BaseFormSet, inlineformset_factory

TIME_FORMATS = [
  '%H:%M:%S',
  '%H:%M',
  '%Hh%M',
  '%Hh %M',
  '%Hh %Mm %Ss',
  '%Mmin %Ss',
  '%Mmin',
]

class SportSessionForm(forms.ModelForm):
  time = forms.TimeField(input_formats=TIME_FORMATS, widget=forms.TextInput(attrs={'placeholder':'hh:mm'}), required=False)
  distance = forms.FloatField(localize=True, widget=forms.TextInput(attrs={'placeholder': 'km'}), required=False)

  class Meta:
    model = SportSession
    fields = ('sport', 'distance', 'time')
    widgets = {
      'sport' : forms.HiddenInput(),
    }

  def __init__(self, multi_sports, default_sport, *args, **kwargs):
    super(SportSessionForm, self).__init__(*args, **kwargs)

    self.sports = []
    if multi_sports:
      # Load only sports of depth 1 for this form
      self.sports = Sport.objects.filter(depth=1)
      self.fields['sport'].queryset = self.sports
    else:
      # No sport choice when multi_sports is disabled
      del self.fields['sport']

    # Apply default sport to instance
    if not hasattr(self.instance, 'sport'):
      self.instance.sport = default_sport

  def clean(self, *args, **kwargs):
    super(SportSessionForm, self).clean(*args, **kwargs)

    if 'distance' in self.cleaned_data and self.cleaned_data['distance'] is None \
      and 'time' in self.cleaned_data and self.cleaned_data['time'] is None:
      raise forms.ValidationError('Spécifiez une distance ou un temps pour ajouter un sport.')

    return self.cleaned_data


class SportWeekForm(forms.ModelForm):
  class Meta:
    model = SportWeek
    fields = ('comment', )

class SportDayForm(forms.ModelForm):
  nb_extras = 4

  class Meta:
    model = SportDay
    fields = ('name', 'comment', 'type', 'race_category')
    widgets = {
      'type' : forms.HiddenInput(),
    }

  def __init__(self, data=None, week=None, date=None, *args, **kwargs):
    self.week = week
    self.date = date

    # Base init
    super(SportDayForm, self).__init__(data, *args, **kwargs)
    if not self.prefix:
      self.prefix = 'day'


  def clean(self):
    data = super(SportDayForm, self).clean()

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

    return data

  def save(self, *args, **kwargs):
    # Save day
    day = super(SportDayForm, self).save(commit=False, *args, **kwargs)
    if self.week:
      day.week = self.week
    if self.date:
      day.date = self.date
    day.save()

    return day

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
    if SportDay.objects.filter(report__user=self.user, date=self.cleaned_data['date']):
      raise forms.ValidationError('Une séance existe déjà à cette date.')

    return self.cleaned_data['date']
